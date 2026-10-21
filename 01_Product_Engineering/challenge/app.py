"""The server.

`gradio.Server` is a FastAPI app with Gradio's API engine bolted in. You get
queueing, streaming, and MCP for free, but you bring your own frontend. That
split is the point: the API is the product, the UI is disposable.
"""

import base64
import binascii
import csv
import os
import re
import secrets
from datetime import date, timedelta
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path
from typing import NamedTuple

from fastapi import HTTPException
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from gradio import Server
from pydantic import ValidationError

from llm import stream_reply, UnreadableDocument, extract_fields
from schema import DocType, ImportRecord, InvoiceExtraction, Request, Response

app = Server()

# Optional HTTP basic auth for hosted copies: off unless APP_PASSWORD is set.
# /health stays open because a load balancer's health check can't log in, and
# Gradio calls its own startup-events route from localhost during launch.
APP_USERNAME = os.getenv("APP_USERNAME", "demo")
APP_PASSWORD = os.getenv("APP_PASSWORD")


def _auth_exempt(request) -> bool:
    if request.url.path == "/health":
        return True
    local = request.client is not None and request.client.host in ("127.0.0.1", "::1")
    return local and request.url.path == "/gradio_api/startup-events"


@app.middleware("http")
async def basic_auth(request, call_next):
    if APP_PASSWORD and not _auth_exempt(request):
        expected = "Basic " + base64.b64encode(f"{APP_USERNAME}:{APP_PASSWORD}".encode()).decode()
        if not secrets.compare_digest(request.headers.get("authorization", ""), expected):
            return PlainTextResponse("Login required", status_code=401,
                                     headers={"WWW-Authenticate": 'Basic realm="Auto Invoicing"'})
    return await call_next(request)

FRONTEND = Path(__file__).parent / "frontend" / "index.html"
SAMPLES = Path(__file__).parent / "samples"

_MAX_FUTURE_DAYS = 30
COMPANY = "Example Company LLC"
ACCOUNTANT_MAP: dict[str, str] = {}  # folder shortname -> full name

VENDORS_CSV = os.getenv("VENDORS_CSV", str(Path(__file__).parent / "vendors.csv"))
FUZZY_THRESHOLD = float(os.getenv("VENDOR_MATCH_THRESHOLD", "0.8"))
PHONE_NAME_FLOOR = float(os.getenv("VENDOR_PHONE_NAME_FLOOR", "0.5"))
_PHONE_COLUMNS = ("phone_1", "phone_2", "phone_3")


# --- The API -----------------------------------------------------------------
# The `-> str` return annotation is REQUIRED. Without it Gradio infers zero
# output components and silently returns nothing. Ask us how we know.


@app.api(name="chat")
def chat(message: str, history: list | None = None) -> str:
    """Stream a reply to one user message."""
    yield from stream_reply(message, history)


class VendorMatch(NamedTuple):
    vendor_id: str  # "" when unmatched
    vendor_name: str
    recognition: str  # the phone number or name the match used
    method: str  # "phone" | "fuzzy_name" | "none"
    phone_rejected: str = ""  # vendor whose phone matched a bill naming someone else


class _Vendor(NamedTuple):
    vendor_id: str
    vendor_name: str
    phones: tuple[str, ...]  # digits only; may carry the vendor master's trailing-zero padding


def _normalize_phone(raw: str) -> str:
    """Digits only; drop a leading US country code. "+1 (580) 555-0123" -> "5805550123"."""
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 11 and digits.startswith("1"):
        return digits[1:]
    return digits


def _name_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


@lru_cache(maxsize=1)
def _vendors() -> tuple[_Vendor, ...]:
    """Load the vendor master once. Expects active vendors for one company only."""
    with open(VENDORS_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    vendors = []
    for row in rows:
        phones = tuple(
            digits
            for col in _PHONE_COLUMNS
            if (digits := re.sub(r"\D", "", row.get(col) or "")) and digits.strip("0")
        )
        vendors.append(_Vendor(row["vendor_id"].strip(), row["vendor_name"], phones))
    return tuple(vendors)


def match_vendor(vendor_name: str, vendor_phone: str | None) -> VendorMatch:
    """Vendor master lookup: phone first, then fuzzy name. Production's rules except where noted."""
    vendors = _vendors()

    # 1. Phone: prefix match, because the vendor master pads numbers with trailing
    #    zeros ("58023746910000"). Shared numbers go to the closest name. Fewer
    #    than 10 digits is a fragment that would prefix-match the wrong vendor,
    #    so it falls through to the name match. (Differs from production; filed.)
    #    A hit whose name scores below PHONE_NAME_FLOOR is no match, and the name
    #    match isn't tried: phone and name point at different vendors, so a
    #    person decides. In production an accountant sees the name; an ok result
    #    here gets no look. (Differs from production.)
    digits = _normalize_phone(vendor_phone or "")
    if len(digits) >= 10:
        hits = [v for v in vendors if any(p.startswith(digits) for p in v.phones)]
        if hits:
            best = max(hits, key=lambda v: _name_similarity(vendor_name, v.vendor_name))
            if _name_similarity(vendor_name, best.vendor_name) < PHONE_NAME_FLOOR:
                return VendorMatch("", vendor_name, "", "none", best.vendor_name)
            return VendorMatch(best.vendor_id, best.vendor_name, vendor_phone, "phone")

    # 2. Fuzzy name: best ratio wins, accepted at or above the threshold.
    best, best_ratio = None, 0.0
    for v in vendors:
        ratio = _name_similarity(vendor_name, v.vendor_name)
        if ratio > best_ratio:
            best, best_ratio = v, ratio
    if best is not None and best_ratio >= FUZZY_THRESHOLD:
        return VendorMatch(best.vendor_id, best.vendor_name, vendor_name, "fuzzy_name")

    return VendorMatch("", vendor_name, "", "none")


@app.api(name="extract_invoice_record")
def extract_invoice_record(pdf_b64: str, processing_id: str,
                           accountant_shortname: str, source_key: str) -> str:
    """Read one invoice or credit memo PDF and return a single import-ready record; posts nothing.

    Args:
        pdf_b64: The PDF file, base64-encoded. Scanned or digital.
        processing_id: Caller's unique ID for this run; ties the result to its audit files.
        accountant_shortname: Name of the drop folder the file came from.
        source_key: Storage path of the original file, echoed back so a reviewer can open it.

    Returns:
        JSON with status (ok | vendor_unmatched | failed), record, extraction, errors, warnings.
    """
    try:
        pdf_bytes = base64.b64decode(pdf_b64, validate=True)
    except (binascii.Error, ValueError):
        return _failed(source_key, "pdf_b64 is not valid base64").model_dump_json()
    if not pdf_bytes.startswith(b"%PDF"):
        return _failed(source_key, "file is not a PDF").model_dump_json()

    try:
        req = Request(pdf_bytes=pdf_bytes, processing_id=processing_id,
                      accountant_shortname=accountant_shortname, source_key=source_key)
    except ValidationError as e:
        return _failed(source_key, f"invalid request: {e}").model_dump_json()

    return build_response(req).model_dump_json()


def build_response(req: Request) -> Response:
    """Steps 2-4. Document problems return status=failed; system errors raise."""
    # 2. Model call
    try:
        ext = extract_fields(req.pdf_bytes)
    except UnreadableDocument as e:
        return _failed(req.source_key, f"model could not read the document: {e}")

    # Credit memos keep a positive total; the printed minus only marks the credit.
    total = abs(ext.invoice_total) if ext.doc_type == DocType.CREDIT_MEMO else ext.invoice_total

    errors = []
    if not ext.vendor_name.strip():
        errors.append("vendor_name is blank")
    if ext.invoice_date > date.today() + timedelta(days=_MAX_FUTURE_DAYS):
        errors.append(f"invoice_date {ext.invoice_date} is over {_MAX_FUTURE_DAYS} days ahead")
    if total < 0:
        errors.append(f"negative total {total} on an Invoice: reversal, enter by hand")
    elif total == 0:
        errors.append("total is zero")
    # The printed lines are a second reading of the total. Signed on an Invoice,
    # so a credit read as one doesn't pass; a credit memo may print its lines
    # without the minus its total carries, so there only the amount must agree.
    # No lines fails rather than skips the check, or a model that drops them
    # would wave any total through. The lines leave out a statement's previous
    # balance and payments, so a statement carrying an unpaid balance fails
    # instead of posting that balance a second time.
    if not ext.line_items:
        errors.append("no line items to check the total against")
    else:
        lines_sum = sum(li.amount for li in ext.line_items)
        if ext.doc_type == DocType.CREDIT_MEMO:
            agree = abs(lines_sum) == abs(ext.invoice_total)
        else:
            agree = lines_sum == ext.invoice_total
        if not agree:
            errors.append(f"line items sum to {lines_sum}, total is {ext.invoice_total}")
    if errors:
        return _failed(req.source_key, *errors, extraction=ext)

    warnings = []
    if ext.due_date and ext.due_date < ext.invoice_date:
        warnings.append(f"due_date {ext.due_date} is before invoice_date {ext.invoice_date}")

    # 3. Vendor match. Lookup outages raise; no match is a status, not an error.
    match = match_vendor(ext.vendor_name, ext.vendor_phone)
    status = "ok"
    if match.phone_rejected:
        status = "vendor_unmatched"
        warnings.append(f"phone {ext.vendor_phone} is {match.phone_rejected!r}'s, but the bill "
                        f"names {ext.vendor_name!r}; vendor_id left blank")
    elif match.method == "none":
        status = "vendor_unmatched"
        warnings.append(f"no vendor master match for {ext.vendor_name!r}; vendor_id left blank")

    batch_no = req.processing_id.replace("-", "")[:12]
    # A generated number comes from the document, never the run: the same bill
    # must get the same number every time, or the ERP's duplicate check misses it.
    # The account number goes first when printed, as in the accountants' utility
    # scheme, so one utility's same-day bills for several accounts don't collide.
    number = (ext.invoice_number or "").strip()
    stem = re.sub(r"[^0-9A-Za-z]", "", ext.account_number or "") or match.vendor_id
    generated = []
    if not number and stem:
        number = f"{stem}{ext.invoice_date:%m%d%y}"
        generated.append("invoice_number")
        warnings.append(f"no invoice number on document; generated {number} "
                        "(accountants' scheme not known yet)")
    elif not number:
        warnings.append("no invoice number on document and no account number or vendor_id "
                        "to build one from; number left blank")
    if number and ext.doc_type == DocType.CREDIT_MEMO and not number.upper().endswith("CM"):
        number += "CM"

    record = ImportRecord(
        doc_type=ext.doc_type,
        total=total,
        date=ext.invoice_date,
        number=number,
        vendor_id=match.vendor_id,
        vendor_name=match.vendor_name,
        recognition=match.recognition,
        batch_no=batch_no,
        processor=ACCOUNTANT_MAP.get(req.accountant_shortname, req.accountant_shortname),
        group_name=req.accountant_shortname,
        company=COMPANY,
    )

    # 4. Response
    return Response(status=status, record=record, extraction=ext, errors=[],
                    warnings=warnings, generated_fields=generated,
                    vendor_match_method=match.method, source_key=req.source_key)


def _failed(source_key: str, *errors: str,
            extraction: InvoiceExtraction | None = None) -> Response:
    return Response(status="failed", errors=list(errors), extraction=extraction,
                    source_key=source_key)


# --- The frontend ------------------------------------------------------------
# Defining a route at "/" replaces Gradio's default UI with ours.


@app.get("/", response_class=HTMLResponse)
def homepage() -> str:
    return FRONTEND.read_text(encoding="utf-8")


@app.get("/samples/{name}")
def sample(name: str) -> FileResponse:
    """Made-up invoices for the page's "Try a sample" buttons."""
    path = SAMPLES / name
    if path.suffix != ".pdf" or path.parent != SAMPLES or not path.is_file():
        raise HTTPException(status_code=404)
    return FileResponse(path, media_type="application/pdf")


@app.get("/health")
def health() -> dict:
    """Your future ops team will thank you. Load balancers need this."""
    return {"status": "ok", "model": os.getenv("LLM_MODEL", "gpt-4.1-mini")}


if __name__ == "__main__":
    # 0.0.0.0 so the container is reachable from the host. On your laptop this
    # is fine. On a firm network, "reachable from where, exactly?" is the
    # question this challenge wants you to go ask.
    #
    # Read the port rather than hardcoding it, so a machine that already has
    # something on 7860 can move this one without editing code.
    port = int(os.getenv("GRADIO_SERVER_PORT", "7860"))

    # Gradio announces the address it BOUND to, which is 0.0.0.0 -- not an
    # address a browser can open. Windows rejects it outright; macOS and Linux
    # quietly redirect it to localhost, which is why it looks fine on some
    # machines and broken on others. Print the one that always works.
    print(f"\n  Open http://localhost:{port} in your browser\n", flush=True)
    app.launch(server_name="0.0.0.0", server_port=port)
