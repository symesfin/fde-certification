"""Variation axes for the Auto Invoicing synthetic dataset (TC2 Step 1).

Each value comes from something that is the same in all the seeds but varies in
the real queue. Keep in sync with the Variation axes table in
use_case/data/DATASHEET.md.
"""

AXES = {
    # Who produced it and how long it runs; one axis because one-person shops don't send two-page site-grouped bills.
    "source": [
        "an electric or propane co-op's billing system, one page: one meter, an account number but no invoice number, "
        "a service period next to the statement date, a toll-free number and a local office number",
        "an electric or propane co-op's billing system, two pages: ten or more meters grouped by site, the header "
        "repeats on page 2, the closing block on page 2 only, an account number but no invoice number, "
        "toll-free and local office numbers",
        "a feed or supply company's ERP, one page: one to three lines, order, PO, BOL and scale-ticket numbers near "
        "the invoice number, separate phone and fax lines, a remit-to lockbox below the mill address",
        "a feed or supply company's ERP, two pages: ten or more deliveries grouped by site, the header repeats on "
        "page 2, the closing block on page 2 only, order and PO numbers near the invoice number, phone and fax lines",
        "a one-person repair shop or vet practice on a word-processor template, one page: business name only in a "
        "header line, a cell number, a three- or four-digit invoice number, dates with the month name written out, "
        "'Due on receipt' instead of a due date",
    ],
    # Clean PDFs vs scans and faxes: drifting columns, a fax banner's phone and date, misread scored fields.
    "condition": [
        "born-digital PDF: clean text, columns aligned",
        "scanned or faxed: columns run together so labels and amounts drift apart, a fax banner with the sender's "
        "fax number and a transmission date, and OCR swaps a reader can undo, scored fields included: l, O or S "
        "inside the total or an all-digit invoice number, 0 or 1 inside a word of the vendor name; "
        "the expected output is the true value",
    ],
    # What the document is, paired with the decoy it usually carries; sets status and whether the extraction is kept.
    "outcome": [
        "an invoice, nothing near the total that could be mistaken for it; status ok",
        "an invoice with a decoy near the total: a previous balance and payments received, a subtotal before tax "
        "and freight, or a late-payment amount; status ok",
        "a credit memo: titled CREDIT MEMO, cites the original invoice or statement and its amount, or shows a "
        "previous balance; total printed with a trailing minus or in parentheses; "
        "status ok, doc_type CreditMemo, total negative",
        "a reversal: mostly titled plain INVOICE or STATEMENT with the reversal shown only in a reference line "
        "('Reverses invoice ...'), sometimes titled REVERSAL; nothing on it says credit; total negative; "
        "status failed, fields filled in",
        "nothing to extract: a packing slip, delivery or weigh ticket, work order or usage summary with no amount "
        "due, and weights, quantities or meter reads where a total would sit; status failed, extraction null",
    ],
}
# 5 x 2 x 5 = 50 combinations, 20 of them failed
