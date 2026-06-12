import re
from utils.regex_patterns import InvoiceRegex

def parse_invoice_text(text):
    """
    Parses the extracted text using regular expressions to find:
    - Invoice Number
    - Invoice Date
    - Vendor Name
    - GST Number
    - Tax Amount
    - Total Amount
    """
    
    parsed_data = {
        'invoice_number': '',
        'invoice_date': '',
        'vendor_name': '',
        'gst_number': '',
        'tax_amount': 0.0,
        'total_amount': 0.0
    }
    
    # Extract Invoice Number
    inv_match = InvoiceRegex.INVOICE_NUMBER.search(text)
    if inv_match:
        parsed_data['invoice_number'] = inv_match.group(1).strip()
        
    # Extract Date
    date_match = InvoiceRegex.INVOICE_DATE.search(text)
    if date_match:
        parsed_data['invoice_date'] = date_match.group(1).strip()
        
    # Extract GST Number
    gst_match = InvoiceRegex.GST_NUMBER.search(text)
    if gst_match:
        parsed_data['gst_number'] = gst_match.group(1).strip()
        
    # Extract Amounts
    tax_matches = InvoiceRegex.TAX_AMOUNT.findall(text)
    total_matches = InvoiceRegex.TOTAL_AMOUNT.findall(text)
    
    if tax_matches:
        # Take the last match assuming it's the summary at the bottom
        clean_tax = tax_matches[-1].replace(',', '')
        try:
            parsed_data['tax_amount'] = float(clean_tax)
        except ValueError:
            pass
            
    if total_matches:
        # Take the last match assuming it's the final grand total
        clean_total = total_matches[-1].replace(',', '')
        try:
            parsed_data['total_amount'] = float(clean_total)
        except ValueError:
            pass
            
    # Heuristic for Vendor Name: Usually it's in the first few lines of the invoice
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines:
        # Avoid common header words like 'INVOICE'
        for line in lines[:5]:
            if not re.search(r'(?i)invoice|date|number', line) and len(line) > 3:
                parsed_data['vendor_name'] = line
                break

    return parsed_data
