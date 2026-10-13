"""Generate the sample PDFs the page offers under "Try a sample".

Every vendor, address, phone and amount is made up. The vendors that should
match are in vendors.sample.csv; one deliberately isn't. Regenerate with:

    uv run --with reportlab python samples/make_samples.py
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

OUT = Path(__file__).parent
BILL_TO = ["Example Company LLC", "Accounts Payable", "PO Box 100", "Prairieview, OK 73000"]


def header(c, vendor, lines, title, fields):
    w, h = letter
    c.setFont("Helvetica-Bold", 18)
    c.drawString(0.75 * inch, h - 0.9 * inch, vendor)
    c.setFont("Helvetica", 9.5)
    for i, line in enumerate(lines):
        c.drawString(0.75 * inch, h - 1.15 * inch - i * 13, line)
    c.setFont("Helvetica-Bold", 20)
    c.drawRightString(w - 0.75 * inch, h - 0.9 * inch, title)
    c.setFont("Helvetica", 10)
    for i, (k, v) in enumerate(fields):
        y = h - 1.2 * inch - i * 15
        c.drawRightString(w - 2.0 * inch, y, k)
        c.drawRightString(w - 0.75 * inch, y, v)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.75 * inch, h - 2.3 * inch, "BILL TO")
    c.setFont("Helvetica", 10)
    for i, line in enumerate(BILL_TO):
        c.drawString(0.75 * inch, h - 2.5 * inch - i * 13, line)


def table(c, rows, total_label, total, top=3.6):
    w, h = letter
    y = h - top * inch
    c.setFillColor(colors.HexColor("#eef1f5"))
    c.rect(0.75 * inch, y - 4, w - 1.5 * inch, 18, fill=1, stroke=0)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)
    for x, label in [(0.85, "Description"), (4.6, "Qty"), (5.5, "Rate")]:
        c.drawString(x * inch, y, label)
    c.drawRightString(w - 0.85 * inch, y, "Amount")
    c.setFont("Helvetica", 10)
    for i, (desc, qty, rate, amount) in enumerate(rows):
        ry = y - 24 - i * 18
        c.drawString(0.85 * inch, ry, desc)
        c.drawString(4.6 * inch, ry, qty)
        c.drawString(5.5 * inch, ry, rate)
        c.drawRightString(w - 0.85 * inch, ry, amount)
    ty = y - 40 - len(rows) * 18
    c.line(4.5 * inch, ty + 12, w - 0.75 * inch, ty + 12)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(4.6 * inch, ty - 4, total_label)
    c.drawRightString(w - 0.85 * inch, ty - 4, total)
    return ty


def footer(c, text):
    c.setFont("Helvetica-Oblique", 8.5)
    c.setFillColor(colors.HexColor("#666666"))
    c.drawString(0.75 * inch, 0.6 * inch, text)
    c.setFillColor(colors.black)


def propane():
    c = canvas.Canvas(str(OUT / "propane_invoice.pdf"), pagesize=letter)
    header(c, "Prairie Propane Supply",
           ["410 Tank Farm Rd", "Prairieview, OK 73000", "Phone (405) 555-0104"],
           "INVOICE", [("Invoice No.", "PPS-20417"), ("Invoice Date", "09/29/2026"), ("Due Date", "10/29/2026")])
    table(c, [("Propane delivery, Site 14 barn tank", "812 gal", "$1.72", "1,396.64"),
              ("Delivery fee", "1", "$35.00", "35.00"),
              ("Tank rental, Sept", "1", "$18.00", "18.00")],
          "TOTAL DUE", "$1,449.64")
    footer(c, "Sample document for the Auto Invoicing demo. All names and figures are fictitious.")
    c.save()


def feed_with_weigh_ticket():
    c = canvas.Canvas(str(OUT / "feed_invoice_with_weigh_ticket.pdf"), pagesize=letter)
    header(c, "Heartland Feed Company", ["88 Mill St", "Cornfield, OK 73001"],
           "INVOICE", [("Invoice No.", "HF-55812"), ("Invoice Date", "10/02/2026"), ("Terms", "Net 15")])
    table(c, [("Finisher ration, bulk, Site 9", "24.6 ton", "$312.00", "7,675.20"),
              ("Mineral premix", "12 bag", "$21.50", "258.00")],
          "AMOUNT DUE", "$7,933.20")
    footer(c, "Weigh ticket attached. Sample document; all names and figures are fictitious.")
    c.showPage()
    w, h = letter
    c.setFont("Helvetica-Bold", 16)
    c.drawString(0.75 * inch, h - 0.9 * inch, "WEIGH TICKET  No. 30177")
    c.setFont("Helvetica", 11)
    for i, line in enumerate(["Date: 10/01/2026", "Truck: 14   Driver: J. Sample",
                              "Gross: 78,420 lb", "Tare: 29,220 lb", "Net: 49,200 lb (24.6 ton)",
                              "Product: Finisher ration", "Destination: Site 9"]):
        c.drawString(0.75 * inch, h - 1.4 * inch - i * 18, line)
    footer(c, "Sample document; all names and figures are fictitious.")
    c.save()


def credit_memo():
    c = canvas.Canvas(str(OUT / "grain_credit_memo.pdf"), pagesize=letter)
    header(c, "Midwest Grain Coop", ["1 Elevator Rd", "Prairieview, OK 73000", "Phone (405) 555-0105"],
           "CREDIT MEMO", [("Credit Memo No.", "MG-7731"), ("Date", "10/05/2026"), ("Ref. Invoice", "MG-7650")])
    table(c, [("Return: damaged bags, corn screenings", "10 bag", "$12.50", "125.00-")],
          "CREDIT TOTAL", "125.00-")
    footer(c, "Credit applies to your account. Sample document; all names and figures are fictitious.")
    c.save()


def unknown_utility():
    c = canvas.Canvas(str(OUT / "utility_bill_unknown_vendor.pdf"), pagesize=letter)
    header(c, "Sandhill Electric Membership Corp", ["PO Box 2200", "Dunes, OK 73002"],
           "STATEMENT", [("Account No.", "4471-0098-12"), ("Statement Date", "10/03/2026"), ("Due Date", "10/24/2026")])
    table(c, [("Service: Site 22 grow-finish barn, meter 88123", "6,240 kWh", "$0.094", "586.56"),
              ("Customer charge", "1", "$32.00", "32.00")],
          "AMOUNT DUE", "$618.56")
    footer(c, "This statement has no invoice number. Sample document; all names and figures are fictitious.")
    c.save()


def reversal():
    c = canvas.Canvas(str(OUT / "reversal_negative_total.pdf"), pagesize=letter)
    header(c, "River Valley Electric Cooperative", ["300 Line Ave", "Rivertown, OK 73003", "Phone (405) 555-0107"],
           "INVOICE", [("Invoice No.", "RV-1188-RV"), ("Invoice Date", "10/04/2026"), ("Reverses", "RV-1188")])
    table(c, [("Reversal of duplicate billing, Site 5", "1", "-$89.50", "-89.50")],
          "TOTAL", "-$89.50")
    footer(c, "Sample document; all names and figures are fictitious.")
    c.save()


if __name__ == "__main__":
    for make in (propane, feed_with_weigh_ticket, credit_memo, unknown_utility, reversal):
        make()
    print("\n".join(sorted(p.name for p in OUT.glob("*.pdf"))))
