from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from models.invoice_model import InvoiceModel

def export_invoices_to_pdf(output_path):
    """
    Exports all invoice records to a PDF report.
    Returns the path to the generated PDF.
    """
    invoices = InvoiceModel.get_all_invoices()
    
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    elements = []
    
    # Title
    styles = getSampleStyleSheet()
    title = Paragraph("Electronic Invoicing System - Report", styles['Title'])
    elements.append(title)
    
    # Table Data
    data = [['ID', 'Invoice No', 'Date', 'Vendor', 'GST No', 'Tax', 'Total']]
    
    for inv in invoices:
        vendor = inv.get('vendor_name') or ''
        vendor_display = vendor[:15] + '...' if len(vendor) > 15 else vendor
        data.append([
            str(inv.get('id', '')),
            inv.get('invoice_number') or 'N/A',
            inv.get('invoice_date') or 'N/A',
            vendor_display or 'N/A',
            inv.get('tax_number') or 'N/A',
            f"{inv.get('gst_amount') or 0.0:.2f}",
            f"{inv.get('grand_total') or 0.0:.2f}"
        ])
        
    # Table Style
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    return output_path
