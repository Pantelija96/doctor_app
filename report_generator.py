import os
import sys
import base64
import tempfile
import webbrowser
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# === Font setup ===
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

# === Main PDF generator ===
def generate_appointment_pdf(patient_data, diagnose_text, logo_path=None):
    font_path = resource_path("assets/DejaVuSans.ttf")
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
    else:
        raise FileNotFoundError("Font file not found at: " + font_path)
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

# === New function for daily report PDF ===
def generate_day_report_pdf(patient_list, selected_date, logo_path=None):
    font_path = resource_path("assets/DejaVuSans.ttf")
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
    else:
        raise FileNotFoundError("Font file not found at: " + font_path)
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)

    # === Styles ===
    base_style = {
        "fontName": "DejaVuSans",
        "fontSize": 13,
        "leading": 18,
    }
    table_paragraph_style = ParagraphStyle("TableText", fontName="DejaVuSans", fontSize=10, leading=12, alignment=TA_LEFT)

    elements = []

    # === Logo and header ===
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image(logo_path, width=128, height=45)
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
        Paragraph("Dnevni izveštaj : "+selected_date, ParagraphStyle("Title", **{
            **base_style,
            "fontSize": 18,
            "alignment": TA_CENTER,
            "spaceAfter": 20
        }))
    )

    # === Patient Table ===
    # Prepare table data: Order, Full Name, Phone Number, Birthday
    table_data = [["#", "Ime i prezime", "Broj telefona", "Datum rođenja"]]
    for patient in patient_list:
        order = str(patient.get("order", ""))
        full_name = Paragraph(patient.get("full_name", ""), table_paragraph_style)
        phone_number = Paragraph(patient.get("phone_number", "/"), table_paragraph_style)
        birthday = Paragraph(patient.get("birthday", ""), table_paragraph_style)
        table_data.append([order, full_name, phone_number, birthday])

    # Create table with adjusted column widths
    table = Table(table_data, colWidths=[50, 200, 120, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (1, 1), (3, -1), 5),
        ('RIGHTPADDING', (1, 1), (3, -1), 5),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 40))

    # === Footer ===
    footer_text = (
        "Pacijent je obavešten o dijagnozi, prognozi, vremenu trajanja i uspešnosti lečenja i pristaje na predloženu medicinsku meru. "
        "Predočene su mu eventualne posledice preuzimanja i ne preuzimanja predložene medicinske mere. "
        "Shodno članu 11 i članovima 15 do 19 Zakona o pravima pacijenata (Sl. glasnik broj 45/2013)."
    )
    elements.append(Spacer(1, 100))
    elements.append(Paragraph(footer_text, ParagraphStyle("Legal", **{**base_style, "alignment": TA_JUSTIFY})))

    # === Build PDF ===
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    # === Save to temporary file and open ===
    pdf_data = base64.b64decode(base64.b64encode(pdf).decode("utf-8"))
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        f.write(pdf_data)
        temp_path = f.name
    webbrowser.open(f"file:///{temp_path.replace(os.sep, '/')}")

    return base64.b64encode(pdf).decode("utf-8")