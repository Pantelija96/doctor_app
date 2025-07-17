import base64
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
import os

# === Font setup ===
FONT_PATH = os.path.join("assets", "DejaVuSans.ttf")
if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont("DejaVuSans", FONT_PATH))
else:
    raise FileNotFoundError("Font file not found at: " + FONT_PATH)

# === Main PDF generator ===
def generate_appointment_pdf(patient_data, diagnose_text, logo_path=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)

    # === Styles ===
    base_style = {
        "fontName": "DejaVuSans",
        "fontSize": 13,
        "leading": 18,
    }

    elements = []

    # === Logo and header ===
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image(logo_path, width=128, height=45)  # maintains logo aspect ratio
            logo_table = Table([[logo]], colWidths=[128])
            logo_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            elements.append(logo_table)
        except Exception:
            pass

    # Contact Info
    elements += [
        Paragraph("Grocka, Bulevar Oslobođenja 56", ParagraphStyle("Header", **base_style)),
        Paragraph("Tel: 011 850 35 50, 063 425 827", ParagraphStyle("Header2", **base_style)),
        Paragraph("E-mail: vpavlovic.ordinacija@gmail.com", ParagraphStyle("Header3", **base_style)),
        Paragraph("PIB: 103707526", ParagraphStyle("Header4", **base_style)),
        Spacer(1, 18),
    ]

    # === Title ===
    elements.append(
        Paragraph("Lekarski izveštaj", ParagraphStyle("Title", **{
            **base_style,
            "fontSize": 18,
            "alignment": TA_CENTER,
            "spaceAfter": 20
        }))
    )

    # === Patient Data ===
    elements += [
        Paragraph(
            f"<b>Ime, prezime i datum rođenja:</b> {patient_data.get('full_name', '')}, {patient_data.get('birthday', '')}",
            ParagraphStyle("Body1", **base_style)),
        Paragraph(f"<b>Adresa:</b> {patient_data.get('address', '')}", ParagraphStyle("Body2", **base_style)),
        Spacer(1, 12),

        Paragraph("<b>Uputna dijagnoza:</b>", ParagraphStyle("DiagTitle", **base_style)),
        Spacer(1, 6),
        Paragraph(diagnose_text.replace("\n", "<br />"), ParagraphStyle("DiagText", **base_style)),
        Spacer(1, 40),

        Paragraph("Datum i mesto: ____________________________         Lekar: ____________________________",
                  ParagraphStyle("Date", **base_style)),

        Spacer(1, 100),  # This will help push the footer down; tweak if necessary
    ]

    # === Footer at the bottom ===
    footer_text = (
        "Pacijent je obavešten o dijagnozi, prognozi, vremenu trajanja i uspešnosti lečenja i pristaje na predloženu medicinsku meru. "
        "Predočene su mu eventualne posledice preuzimanja i ne preuzimanja predložene medicinske mere. "
        "Shodno članu 11 i članovima 15 do 19 Zakona o pravima pacijenata (Sl. glasnik broj 45/2013)."
    )

    elements.append(Spacer(1, 100))  # You can fine-tune this height
    elements.append(Paragraph(footer_text, ParagraphStyle("Legal", **{**base_style, "alignment": TA_JUSTIFY})))

    # === Build PDF ===
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return base64.b64encode(pdf).decode("utf-8")
