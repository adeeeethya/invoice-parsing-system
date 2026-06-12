import re
import logging
from .ai_extractor import AIExtractor

logger = logging.getLogger(__name__)

class Extractor:
    def __init__(self):
        # Initialize AI Extractor
        self.ai_extractor = AIExtractor()
        
        # Currency mappings
        self.CURRENCY_MAP = {
            r'(?i)₹|rs\.?|inr': 'INR',
            r'(?i)\$|usd': 'USD',
            r'(?i)€|eur': 'EUR',
            r'(?i)£|gbp': 'GBP',
            r'(?i)¥|jpy': 'JPY',
            r'(?i)aed': 'AED',
            r'(?i)sgd': 'SGD',
            r'(?i)cad': 'CAD',
            r'(?i)aud': 'AUD'
        }
        
        # Regex for amounts allowing currencies, spaces, dots, commas
        amount_pattern = r'([\d,]+\.\d{1,2}|[\d,]+)'
        currency_separators = r'[\s:$€£₹¥a-z\.\-]*'
        
        self.PATTERNS = {
            'invoice_number': re.compile(r'(?i)(?:inv(?:oice)?[\s]*(?:no|number|#)?)[\s]*[:\-]?[\s]*\[?([A-Z0-9\-\/]+)\]?'),
            'invoice_date': re.compile(r'(?i)(?:date)[\s]*[:\-]?[\s]*([0-9]{1,4}[\/\-\.][a-zA-Z0-9]{2,10}[\/\-\.][0-9]{1,4})'),
            'tax_number': re.compile(r'(?i)(?:gst(?:in)?|tax id|vat)[\s#:\-]*([0-9A-Z]{10,15})'),
            
            # Amount fields
            'grand_total': re.compile(rf'(?i)(?:grand total|total amount|amount payable|net amount|invoice total|bill amount|total){currency_separators}{amount_pattern}'),
            'subtotal': re.compile(rf'(?i)(?:subtotal|sub-total|sub total){currency_separators}{amount_pattern}'),
            'gst_amount': re.compile(rf'(?i)(?:tax(?!\s+rate)|gst|vat){currency_separators}{amount_pattern}'),
            'cgst': re.compile(rf'(?i)(?:cgst){currency_separators}{amount_pattern}'),
            'sgst': re.compile(rf'(?i)(?:sgst){currency_separators}{amount_pattern}'),
            'igst': re.compile(rf'(?i)(?:igst){currency_separators}{amount_pattern}')
        }

    def detect_currency(self, text):
        for pattern, curr_code in self.CURRENCY_MAP.items():
            if re.search(pattern, text):
                return curr_code
        return 'USD' # Default if nothing found

    def clean_amount(self, amount_str):
        if not amount_str:
            return 0.0
        # Remove commas, currency symbols, and spaces
        cleaned = re.sub(r'[^\d\.]', '', amount_str)
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    def fallback_extract_line_items(self, lines):
        """
        Parses text lines to identify item description, qty, unit price, total price.
        Groups numbers following a text line.
        """
        items = []
        
        # Identify boundaries
        footer_index = len(lines)
        for i, line in enumerate(lines):
            if re.search(r'(?i)subtotal|sub-total|grand total|total amount|amount due|payment terms|bank details|tax rate', line):
                footer_index = i
                break
                
        start_index = 0
        for i, line in enumerate(lines):
            if re.search(r'(?i)description|item|particulars|qty|rate|amount|price|total', line):
                start_index = i + 1
                break
        if start_index == 0:
            start_index = min(5, len(lines)) # default fallback start
            
        current_desc = None
        current_numbers = []
        
        for line in lines[start_index:footer_index]:
            line = line.strip()
            if not line:
                continue
                
            # Skip lines containing typical header/footer keywords
            if re.search(r'(?i)invoice|date|gstin|tax id|vat|phone|mobile|email|address|bill to|ship to|vendor|customer|client', line):
                continue
                
            # Check if line is numeric (with optional currency symbol/parentheses/brackets)
            is_numeric = re.match(r'^\s*[\[\(]?\s*[\d,]+(?:\.\d+)?\s*[\]\)]?\s*$', line)
            # An item code is typically an integer without a decimal point that is long or bracketed
            is_item_code = '[' in line or '(' in line or (is_numeric and '.' not in line and len(line) > 4)
            
            if is_numeric and not is_item_code:
                val = self.clean_amount(line)
                if current_desc:
                    current_numbers.append(val)
            elif not is_numeric and len(line) >= 3:
                # Save previous item if we have description and numbers
                if current_desc and current_numbers:
                    items.append({
                        'description': current_desc,
                        'numbers': current_numbers
                    })
                current_desc = line
                current_numbers = []
                
        # Append last item
        if current_desc and current_numbers:
            items.append({
                'description': current_desc,
                'numbers': current_numbers
            })
            
        # Post-process items to extract Qty, Unit Price, Total Price
        parsed_items = []
        for item in items:
            desc = item['description']
            nums = item['numbers']
            
            qty = 1.0
            unit_price = 0.0
            total_price = 0.0
            
            if len(nums) >= 3:
                qty = nums[0]
                unit_price = nums[1]
                total_price = nums[2]
            elif len(nums) == 2:
                val1 = nums[0]
                val2 = nums[1]
                if val1 == val2:
                    qty = 1.0
                    unit_price = val1
                    total_price = val2
                elif val1 <= 100 and val1 > 0:
                    qty = val1
                    total_price = val2
                    unit_price = total_price / qty if qty else 0.0
                else:
                    unit_price = val1
                    total_price = val2
                    qty = total_price / unit_price if unit_price else 1.0
            elif len(nums) == 1:
                total_price = nums[0]
                unit_price = total_price
                qty = 1.0
                
            if total_price == 0.0:
                continue
                
            parsed_items.append({
                'description': desc,
                'quantity': qty,
                'unit_price': unit_price,
                'total_price': total_price
            })
            
        return parsed_items

    def extract(self, text, lines):
        # 1. Try Gemini AI Extraction first
        if self.ai_extractor.is_available():
            logger.info("Using Gemini AI for invoice extraction.")
            ai_data = self.ai_extractor.extract(text, lines)
            if ai_data:
                return ai_data
            logger.warning("Gemini AI extraction failed, falling back to regex extraction.")

        # 2. Regex and heuristic fallback
        data = {
            'vendor_name': '',
            'invoice_number': '',
            'invoice_date': '',
            'tax_number': '',
            'currency': self.detect_currency(text),
            'subtotal': 0.0,
            'gst_amount': 0.0,
            'cgst': 0.0,
            'sgst': 0.0,
            'igst': 0.0,
            'grand_total': 0.0,
            'raw_ocr_text': text,
            'line_items': []
        }
        
        inv_match = self.PATTERNS['invoice_number'].search(text)
        if inv_match:
            data['invoice_number'] = inv_match.group(1).strip()
            
        date_match = self.PATTERNS['invoice_date'].search(text)
        if date_match:
            data['invoice_date'] = date_match.group(1).strip()
            
        tax_match = self.PATTERNS['tax_number'].search(text)
        if tax_match:
            data['tax_number'] = tax_match.group(1).strip()
            
        # Vendor Name Heuristic (First line without keywords, max 50 chars)
        for line in lines[:10]:
            if not re.search(r'(?i)invoice|date|number', line) and 3 < len(line.strip()) < 50:
                data['vendor_name'] = line.strip()
                break

        # Extract Multiple Totals and pick the largest
        grand_totals = []
        for match in self.PATTERNS['grand_total'].findall(text):
            grand_totals.append(self.clean_amount(match))
        
        if grand_totals:
            data['grand_total'] = max(grand_totals)

        # Subtotal
        sub_matches = self.PATTERNS['subtotal'].findall(text)
        if sub_matches:
            data['subtotal'] = self.clean_amount(sub_matches[-1])

        # GST, CGST, SGST, IGST
        for tax_type in ['gst_amount', 'cgst', 'sgst', 'igst']:
            matches = self.PATTERNS[tax_type].findall(text)
            if matches:
                data[tax_type] = self.clean_amount(matches[-1])
                
        # Validation
        if data['grand_total'] < data['subtotal']:
            data['grand_total'], data['subtotal'] = data['subtotal'], data['grand_total']

        # Extract line items via fallback logic
        data['line_items'] = self.fallback_extract_line_items(lines)

        return data
