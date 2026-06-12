import os
import requests
import json
import logging
from dotenv import load_dotenv

# Load env variables from .env
load_dotenv()

logger = logging.getLogger(__name__)

class AIExtractor:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = "gemini-2.5-flash"
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def is_available(self):
        return bool(self.api_key)

    def extract(self, raw_text, lines):
        if not self.is_available():
            logger.warning("GEMINI_API_KEY not found in environment. AI Extraction disabled.")
            return None

        joined_lines = "\n".join(lines)
        prompt = f"""You are an expert invoice parser. Parse the following OCR-extracted text from an invoice and return a structured JSON object matching the requested schema.

OCR Extracted Text:
---
{raw_text}
---

Text Lines:
---
{joined_lines}
---

Ensure all numeric amounts are parsed as numbers. If any field is not found, return an empty string for strings, or 0.0 for numbers.
For currency, map it to a standard 3-letter currency code (e.g. INR, USD, EUR, GBP).
For line_items, extract each item's description, quantity, unit_price, and total_price."""

        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": {
                    "type": "OBJECT",
                    "properties": {
                        "vendor_name": {"type": "STRING"},
                        "invoice_number": {"type": "STRING"},
                        "invoice_date": {"type": "STRING"},
                        "tax_number": {"type": "STRING"},
                        "currency": {"type": "STRING"},
                        "subtotal": {"type": "NUMBER"},
                        "gst_amount": {"type": "NUMBER"},
                        "cgst": {"type": "NUMBER"},
                        "sgst": {"type": "NUMBER"},
                        "igst": {"type": "NUMBER"},
                        "grand_total": {"type": "NUMBER"},
                        "line_items": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "description": {"type": "STRING"},
                                    "quantity": {"type": "NUMBER"},
                                    "unit_price": {"type": "NUMBER"},
                                    "total_price": {"type": "NUMBER"}
                                },
                                "required": ["description", "total_price"]
                            }
                        }
                    },
                    "required": ["grand_total"]
                }
            }
        }

        try:
            url = f"{self.endpoint}?key={self.api_key}"
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Gemini API returned status code {response.status_code}: {response.text}")
                return None
                
            response_json = response.json()
            candidate = response_json.get("candidates", [{}])[0]
            text_response = candidate.get("content", {}).get("parts", [{}])[0].get("text", "")
            
            if not text_response:
                logger.error("Empty text response from Gemini API.")
                return None
                
            parsed_data = json.loads(text_response.strip())
            # Inject raw_ocr_text for compliance with the rest of the application
            parsed_data["raw_ocr_text"] = raw_text
            return parsed_data
            
        except Exception as e:
            logger.error(f"Exception during Gemini AI extraction: {e}")
            return None
