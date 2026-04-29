from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas
import os
from datetime import datetime

INVOICES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "factures")

RESTAURANT_INFO = {
    "name": "PRISCILIA RESTAURANT",
    "address": "Avenue de l'Independance, Yaounde, Cameroun",
    "phone": "+237 6XX XXX XXX",
    "email": "contact@priscilia-restaurant.cm",
    "niu": "NIU: MXXXXXXXX",
    "rccm": "RCCM: RC/YAO/XXXX/B/XXXX"
}

def format_price(amount):
    return "{:,.0f} FCFA".format(amount).replace(",", " ")

def generate_invoice(invoice_data):
    os.makedirs(INVOICES_DIR, exist_ok=True)
    invoice_number = invoice_data['invoice_number']
    filename = os.path.join(INVOICES_DIR, f"Facture_{invoice_number}.pdf")

    doc = SimpleDocTemplate(filename, pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=15*mm, bottomMargin=15*mm)

    styles = getSampleStyleSheet()
    story = []

    # ---- HEADER ----
    title_style = ParagraphStyle('Title', parent=styles['Normal'],
        fontSize=22, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#C8860A'),
        alignment=TA_CENTER, spaceAfter=2)

    sub_style = ParagraphStyle('Sub', parent=styles['Normal'],
        fontSize=9, fontName='Helvetica',
        textColor=colors.HexColor('#555555'),
        alignment=TA_CENTER, spaceAfter=2)

    story.append(Paragraph(RESTAURANT_INFO['name'], title_style))
    story.append(Paragraph(RESTAURANT_INFO['address'], sub_style))
    story.append(Paragraph(f"Tel: {RESTAURANT_INFO['phone']}  |  {RESTAURANT_INFO['email']}", sub_style))
    story.append(Paragraph(f"{RESTAURANT_INFO['niu']}  |  {RESTAURANT_INFO['rccm']}", sub_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#C8860A'), spaceAfter=8))

    # ---- INVOICE INFO ----
    inv_style = ParagraphStyle('InvTitle', parent=styles['Normal'],
        fontSize=16, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#333333'),
        alignment=TA_CENTER, spaceAfter=4)
    story.append(Paragraph(f"FACTURE N° {invoice_number}", inv_style))

    info_style = ParagraphStyle('Info', parent=styles['Normal'],
        fontSize=9, fontName='Helvetica', textColor=colors.HexColor('#444444'))
    right_style = ParagraphStyle('InfoR', parent=styles['Normal'],
        fontSize=9, fontName='Helvetica', textColor=colors.HexColor('#444444'), alignment=TA_RIGHT)

    paid_at = invoice_data.get('paid_at', datetime.now().strftime('%d/%m/%Y %H:%M'))
    table_num = invoice_data.get('table_number', '-')
    client = invoice_data.get('client_name', 'Client')
    serveur = invoice_data.get('serveur', '-')

    info_table = Table([
        [Paragraph(f"<b>Date:</b> {paid_at}", info_style),
         Paragraph(f"<b>Table N°:</b> {table_num}", right_style)],
        [Paragraph(f"<b>Client:</b> {client}", info_style),
         Paragraph(f"<b>Serveur:</b> {serveur}", right_style)],
        [Paragraph(f"<b>Mode de paiement:</b> {invoice_data.get('payment_method','Especes').title()}", info_style), Paragraph("", right_style)],
    ], colWidths=[95*mm, 75*mm])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.HexColor('#FFF8F0'), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 8))

    # ---- ITEMS TABLE ----
    header_style = ParagraphStyle('Hdr', parent=styles['Normal'],
        fontSize=9, fontName='Helvetica-Bold', textColor=colors.white, alignment=TA_CENTER)
    cell_style = ParagraphStyle('Cell', parent=styles['Normal'],
        fontSize=9, fontName='Helvetica', textColor=colors.HexColor('#222222'))
    cell_right = ParagraphStyle('CellR', parent=styles['Normal'],
        fontSize=9, fontName='Helvetica', textColor=colors.HexColor('#222222'), alignment=TA_RIGHT)
    cell_center = ParagraphStyle('CellC', parent=styles['Normal'],
        fontSize=9, fontName='Helvetica', textColor=colors.HexColor('#222222'), alignment=TA_CENTER)

    data = [[
        Paragraph("DESIGNATION", header_style),
        Paragraph("QTE", header_style),
        Paragraph("P.U.", header_style),
        Paragraph("TOTAL", header_style),
    ]]

    for item in invoice_data['items']:
        subtotal = item['quantity'] * item['unit_price']
        data.append([
            Paragraph(item['name'], cell_style),
            Paragraph(str(item['quantity']), cell_center),
            Paragraph(format_price(item['unit_price']), cell_right),
            Paragraph(format_price(subtotal), cell_right),
        ])

    items_table = Table(data, colWidths=[90*mm, 20*mm, 40*mm, 40*mm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#C8860A')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#FFF8F0')]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
        ('LINEBELOW', (0,0), (-1,0), 1.5, colors.HexColor('#A06800')),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 8))

    # ---- TOTALS ----
    tva = invoice_data.get('tva', 0)
    total_ht = invoice_data['total_ht']
    total_ttc = invoice_data['total_ttc']

    totals_data = []
    totals_data.append([Paragraph("<b>Sous-total HT</b>", right_style), Paragraph(format_price(total_ht), right_style)])
    if tva > 0:
        totals_data.append([Paragraph(f"<b>TVA (19.25%)</b>", right_style), Paragraph(format_price(tva), right_style)])
    totals_data.append([Paragraph("<b>TOTAL TTC</b>", ParagraphStyle('TTC', parent=styles['Normal'],
        fontSize=12, fontName='Helvetica-Bold', textColor=colors.white, alignment=TA_RIGHT)),
        Paragraph(format_price(total_ttc), ParagraphStyle('TTCV', parent=styles['Normal'],
        fontSize=12, fontName='Helvetica-Bold', textColor=colors.white, alignment=TA_RIGHT))])

    totals_table = Table(totals_data, colWidths=[120*mm, 50*mm])
    ts = TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('LINEABOVE', (0,-1), (-1,-1), 1, colors.HexColor('#C8860A')),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#C8860A')),
    ])
    totals_table.setStyle(ts)
    story.append(totals_table)

    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#DDDDDD'), spaceAfter=6))

    # ---- FOOTER ----
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'],
        fontSize=8, fontName='Helvetica-Oblique',
        textColor=colors.HexColor('#888888'), alignment=TA_CENTER)
    story.append(Paragraph("Merci de votre visite ! A bientot chez Priscilia Restaurant.", footer_style))
    story.append(Paragraph("Ce document tient lieu de facture officielle.", footer_style))

    doc.build(story)
    return filename
