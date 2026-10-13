"""The Auto Invoicing contract: one dropped PDF in, the accounting ERP record out.

Mirrors the client pipeline's models. Import-record field names are neutral;
the XML writer maps them to the ERP's exact import tags.
"""

from datetime import date
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field


class Request(BaseModel):
    """One file an accountant dropped in their folder."""

    pdf_bytes: bytes = Field(description="The raw PDF, scans included. PDF only.")
    processing_id: str = Field(
        description="Supplied by the caller. Ties the audit files, the dead-letter "
        "message and the shadow comparison together."
    )
    accountant_shortname: str = Field(description="From the folder the file was dropped in.")
    source_key: str = Field(description="Where the PDF lives. The reviewer's link back to it.")


# --- What the model reads off the PDF -----------------------------------------


class LineItem(BaseModel):
    account_number: str
    site_location: str
    description: str
    amount: Decimal = Field(description="Negative for credits.")


class InvoiceExtraction(BaseModel):
    """One per file. A file holding two invoices still yields one: a known gap."""

    doc_type: str = Field(description="Invoice or CreditMemo, read from the document.")
    vendor_name: str
    invoice_number: str | None = Field(
        description="None when the bill has none; the pipeline generates one."
    )
    invoice_total: Decimal = Field(
        description="As printed, sign included. The sign rule lives in the app: a "
        "CreditMemo posts positive; a negative Invoice is a reversal and fails."
    )
    invoice_date: date
    due_date: date | None = None
    vendor_phone: str | None = None
    line_items: list[LineItem] = []
    field_confidences: dict[str, float] = Field(
        default={}, description="Kept for the reviewer. Does not decide the route."
    )


# --- What the pipeline adds ---------------------------------------------------


class MatchMethod(StrEnum):
    PHONE = "phone"
    FUZZY_NAME = "fuzzy_name"
    ADDRESS = "address"
    NONE = "none"


class ImportRecord(BaseModel):
    """One record the accounting ERP imports.

    Dates become MM/DD/YYYY and totals 5,073.05 only when the XML is written.
    """

    doc_type: str = Field(description="Invoice or CreditMemo.")
    total: Decimal
    date: date
    number: str = Field(description='A credit memo gets "CM" appended, as the accountants do.')
    vendor_id: str = Field(description='"" when no vendor matched.')
    vendor_name: str
    recognition: str
    batch_no: str = Field(description="From processing_id.")
    processor: str = Field(description="From the folder, via config.")
    company: str = Field(description="From config.")
    group_name: str = Field(description="From the folder.")


# --- What comes back ----------------------------------------------------------


class Status(StrEnum):
    OK = "ok"  # passed, no warnings
    VENDOR_UNMATCHED = "vendor_unmatched"  # passed, vendor_id blank, flagged
    FAILED = "failed"  # dead-letter queue, with errors


class Response(BaseModel):
    """What comes back for one file."""

    status: Status
    errors: list[str] = []
    warnings: list[str] = []
    extraction: InvoiceExtraction | None = Field(
        default=None, description="None when extraction itself failed."
    )
    record: ImportRecord | None = Field(
        default=None,
        description="One record for the full total, multi-site bills included: the "
        "split goes to the sow production ERP, not this one. None when failed.",
    )

    # For the reviewer. None of this fits in the import XML.
    source_key: str
    generated_fields: list[str] = Field(
        default=[], description="Fields made up rather than read, e.g. invoice_number."
    )
    vendor_match_method: MatchMethod = MatchMethod.NONE


def solve(request: Request) -> Response:
    """Turn one dropped PDF into the accounting ERP record for it.

    Reads the invoice, matches the vendor (phone first, then fuzzy name),
    generates an invoice number when the bill has none, and posts one record
    for the full total, multi-site bills included. A credit memo posts as
    CreditMemo with a positive total and "CM" appended to its number.

    Out of scope for Week 1: splitting multi-site bills by cost center. No PO
    matching; approver assignment and GL coding are Phase 2.
    """
    raise NotImplementedError("implement against this signature")
