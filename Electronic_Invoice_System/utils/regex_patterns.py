import re

class InvoiceRegex:
    # Generic regex for Invoice Number (e.g., INV-1234, #1234, Invoice No: 1234)
    INVOICE_NUMBER = re.compile(r'(?i)(?:inv(?:oice)?[\s]*(?:no|number|#)?)[\s]*[:\-]?[\s]*\[?([A-Z0-9\-\/]+)\]?')
    
    # Regex for Date (e.g., 2023-10-01, 10/01/2023, 10-Jan-2023)
    INVOICE_DATE = re.compile(r'(?i)(?:date)[\s]*[:\-]?[\s]*([0-9]{1,4}[\/\-\.][a-zA-Z0-9]{2,10}[\/\-\.][0-9]{1,4})')
    
    # Generic GST/Tax Number regex
    GST_NUMBER = re.compile(r'(?i)(?:gst(?:in)?|tax id|vat)[\s#:\-]*([0-9A-Z]{10,15})')
    
    # Regex for Total Amount. Restrict characters between keyword and number to spaces, colons, and currency symbols.
    # This prevents matching things like "Total payment due in 30 days" -> 30.
    TOTAL_AMOUNT = re.compile(r'(?i)(?:total|amount due|grand total|balance due)[\s:$€£₹\.\-]*([\d,]+\.\d{1,2})')
    
    # Regex for Tax Amount. Uses negative lookahead to explicitly ignore "TAX RATE".
    TAX_AMOUNT = re.compile(r'(?i)(?:tax(?!\s+rate)|gst|cgst|sgst|igst|vat)[\s:$€£₹\.\-]*([\d,]+\.\d{1,2})')
