# invoice-parser

This is a self-hosted Flask web app that lets you upload image or PDF invoices, runs OCR on them, and extracts the details—like vendor info, tax numbers, totals, and line items—into a MySQL database.

It uses **EasyOCR** for reading document text. For structured field extraction, you can hook it up to the Gemini API (highly recommended), but it also comes with a built-in fallback parser that uses custom regex grouping so it works out of the box without any API configuration.

---

## Setup

### 1. Install dependencies
Set up a virtual environment if you want, and install the libraries:
```bash
pip install -r Electronic_Invoice_System/requirements.txt
```

### 2. Configure MySQL
The app connects to a local MySQL instance. Open `Electronic_Invoice_System/database/db.py` to make sure your credentials match:
- **Host**: `localhost`
- **User**: `root`
- **Password**: `root`
- **Database**: `invoice_db` (this gets created automatically on launch)

### 3. Gemini API Key (Optional)
If you want to use AI extraction, copy `.env.example` to `.env` inside the `Electronic_Invoice_System` folder and add your key:
```env
GEMINI_API_KEY=your_actual_key_here
```
*Note: If no key is set, the app defaults to the local regex parser to extract line items.*

### 4. Run it
```bash
cd Electronic_Invoice_System
python app.py
```
Open `http://127.0.0.1:5000` in your browser.

---

## How it works under the hood

- **OCR Preprocessing**: Uses OpenCV to deskew and scale images before passing them to EasyOCR.
- **Extraction Modes**:
  - **Gemini**: Sends the raw OCR text to `gemini-2.5-flash` with a JSON schema configuration to guarantee clean JSON results.
  - **Regex Fallback**: Uses regex patterns for headers (tax IDs, dates, vendor names) and a vertical-grouping logic that reconstructs lines when table columns get split vertically.
- **Relational Storage**: Saves metadata in the `invoices` table and nested items in `invoice_items` (linked by `invoice_id`).
- **Interactive UI**: The invoice list page includes accordion-style collapsible tables to view line items for each record.
- **Exports**: Quick downloads for CSV and PDF reports.
