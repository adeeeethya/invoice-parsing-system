# Electronic Invoice System (EIS)

A simple, self-hosted web application that extracts key information and line items from invoices (PDFs and images) and saves them in structured tables in a local MySQL database. 

It uses **EasyOCR** and **OpenCV** for document reading and page processing. For structured field extraction, it is designed with a hybrid model: it calls the **Gemini API** for high-accuracy JSON parsing, and falls back to a smart, custom grouping algorithm if you don't configure an API key.

---

## Key Features

- **Document Ingestion**: Upload invoices as `.png`, `.jpg`, `.jpeg`, or `.pdf`.
- **Hybrid Extraction**:
  - **Gemini mode** (`gemini-2.5-flash`): Direct API calls requesting structured JSON matching a predefined schema.
  - **Fallback mode**: A rule-based vertical grouping parser that reconstructs split OCR lines (e.g. associating prices and quantities with the nearest text descriptions).
- **Nested Item Storage**: Invoice headers (vendor, totals, tax numbers) and line items (description, quantity, price) are stored in structured tables with foreign-key cascades in MySQL.
- **Responsive Dashboard**: Summary statistics, monthly charts (using Chart.js), and quick-expand views of recent invoices.
- **Interactive UI**: Expandable rows let you slide down tables of line items directly from the list page.
- **Reporting**: Export your invoices to formatted CSV sheets and PDF tables.

---

## Project Structure

```
├── Electronic_Invoice_System/
│   ├── app.py                      # Flask routes and upload handling
│   ├── database/
│   │   └── db.py                   # DB connection & table initializations
│   ├── exports/
│   │   ├── export_csv.py           # Exports invoices list to CSV
│   │   └── export_pdf.py           # ReportLab code for PDF reports
│   ├── image_processing/
│   │   ├── ai_extractor.py         # REST API wrapper for Gemini structured schema
│   │   ├── extractor.py            # Primary router (AI vs rule-based fallback)
│   │   ├── invoice_processor.py    # OpenCV image deskewing and pre-processing
│   │   └── ocr_engine.py           # EasyOCR text reader configuration
│   ├── models/
│   │   └── invoice_model.py        # Database operations (insertions/searches)
│   ├── templates/                  # Bootstrap frontend layouts
│   ├── utils/                      # Helper methods & regex definitions
│   └── requirements.txt            # Python dependencies list
└── .gitignore                      # Safe git ignores (ignores private keys & uploads)
```

---

## Getting Started

### 1. Prerequisites
Make sure you have **MySQL** running locally and Python 3.9+ installed.

### 2. Configure Database
By default, the application connects to a MySQL instance on `localhost` with:
- **User**: `root`
- **Password**: `root`
- **Database**: `invoice_db` (this is automatically created on launch)

If you need to change these credentials, modify them in `Electronic_Invoice_System/database/db.py`.

### 3. Setup dependencies
Clone the repository, set up a virtual environment, and install the libraries:
```bash
# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r Electronic_Invoice_System/requirements.txt
```

### 4. Setup Gemini API (Optional but recommended)
Rename `.env.example` to `.env` inside the `Electronic_Invoice_System` folder:
```bash
mv Electronic_Invoice_System/.env.example Electronic_Invoice_System/.env
```
Open `.env` and fill in your API key:
```env
GEMINI_API_KEY=AIzaSy...
```
*Note: If this key is missing, the application will automatically fall back to the local regex parser.*

### 5. Run the Server
Start the Flask development server:
```bash
cd Electronic_Invoice_System
python app.py
```
Open `http://127.0.0.1:5000` in your web browser.
