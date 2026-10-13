"""The model calls.

Two functions: stream_reply streams a chat reply, and extract_fields reads one
invoice PDF into an InvoiceExtraction.

Everything provider-specific lives in environment variables, so switching from
OpenAI to Azure to a self-hosted model is a config change, not a code change.
That property matters more than it looks like it does right now -- see the
"Where does this live?" section of the README.
"""

import base64
import json
import os

from litellm import completion
from pydantic import ValidationError

from schema import InvoiceExtraction

# LiteLLM picks the provider from the model string:
#   "gpt-4.1-mini"                    -> OpenAI
#   "azure/my-deployment"             -> Azure OpenAI
#   "anthropic/claude-sonnet-5"       -> Anthropic
#   "ollama/llama3.2"                 -> a model running on your laptop
#   "openai/my-model" + LLM_API_BASE  -> any OpenAI-compatible server (vLLM, LM Studio, ...)
MODEL = os.getenv("LLM_MODEL", "gpt-4.1-mini")
API_BASE = os.getenv("LLM_API_BASE")  # only needed for self-hosted / gateway endpoints
EXTRA_HEADERS = json.loads(os.getenv("LLM_EXTRA_HEADERS") or "{}")

SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "You are a helpful assistant. Be concise and concrete.",
)

EXTRACTION_PROMPT = """Extract these fields from the attached invoice PDF. Return one JSON object with exactly these keys:

- doc_type: "CreditMemo" if the document says credit memo or credit note, otherwise "Invoice".
- vendor_name: the company that sent the document (the seller), not the bill-to, ship-to or remit-to party.
- vendor_phone: the vendor's phone number as printed. If several, the first one. null if none.
- invoice_number: the invoice, statement or credit memo number as printed. Not an account number, a PO number, or a referenced original invoice. null if none.
- invoice_total: the grand total with the sign it has on the document, as a decimal string like "1234.56" or "-51.28". A trailing minus ("51.28-") or parentheses ("(51.28)") mean negative. No currency symbols or thousands separators.
- invoice_date: the document date, YYYY-MM-DD.
- due_date: the payment due date, YYYY-MM-DD. null if none."""


class UnreadableDocument(Exception):
    """The model replied, but the reply isn't a valid InvoiceExtraction."""


def _base_kwargs() -> dict:
    kwargs = {"model": MODEL}
    if API_BASE:
        kwargs["api_base"] = API_BASE
    if EXTRA_HEADERS:
        kwargs["extra_headers"] = EXTRA_HEADERS
    return kwargs


def stream_reply(message: str, history: list[dict] | None = None):
    """Yield the assistant's reply as it arrives, one growing string at a time.

    `history` is a list of {"role": ..., "content": ...} dicts. We rebuild the
    full message list on every turn -- the model is stateless, so the
    conversation only exists because we keep sending it.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history or [])
    messages.append({"role": "user", "content": message})

    reply = ""
    for chunk in completion(**_base_kwargs(), messages=messages, stream=True):
        piece = chunk.choices[0].delta.content
        if piece:
            reply += piece
            yield reply


def extract_fields(pdf_bytes: bytes) -> InvoiceExtraction:
    """Read one invoice PDF and return its fields.

    Raises UnreadableDocument when the reply is empty, isn't JSON, or fails
    validation. Timeouts, rate limits and other provider errors propagate
    unchanged so the caller can retry.
    """
    pdf_data = "data:application/pdf;base64," + base64.b64encode(pdf_bytes).decode(
        "ascii"
    )
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "file",
                    "file": {"filename": "invoice.pdf", "file_data": pdf_data},
                },
                {"type": "text", "text": EXTRACTION_PROMPT},
            ],
        }
    ]

    response = completion(
        **_base_kwargs(),
        messages=messages,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content
    if not content:
        raise UnreadableDocument("model returned an empty reply")

    try:
        return InvoiceExtraction.model_validate_json(content)
    except ValidationError as e:
        raise UnreadableDocument(str(e)) from e
