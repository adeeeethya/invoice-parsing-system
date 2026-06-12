import os
from flask import Flask, render_template, request, redirect, flash, jsonify, send_file, url_for
from werkzeug.utils import secure_filename
from database.db import init_db
from models.invoice_model import InvoiceModel
from utils.helper import allowed_file, pdf_to_images
from image_processing.invoice_processor import process_invoice
from image_processing.ocr_engine import extract_text
from image_processing.extractor import Extractor
from exports.export_csv import export_invoices_to_csv
from exports.export_pdf import export_invoices_to_pdf

app = Flask(__name__)
app.secret_key = "super_secret_key_for_flask"

UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize DB on startup
init_db()

# Initialize Extractor
extractor = Extractor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    stats = InvoiceModel.get_statistics()
    recent = InvoiceModel.get_recent_invoices(5)
    return render_template('dashboard.html', stats=stats, recent=recent)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Processing
            parsed_data = {}
            if filename.lower().endswith('.pdf'):
                images = pdf_to_images(file_path, app.config['UPLOAD_FOLDER'])
                full_text = ""
                all_lines = []
                for img_path in images:
                    preprocessed = process_invoice(img_path)
                    text, lines = extract_text(preprocessed)
                    full_text += text + "\n"
                    all_lines.extend(lines)
                parsed_data = extractor.extract(full_text, all_lines)
            else:
                preprocessed = process_invoice(file_path)
                text, lines = extract_text(preprocessed)
                parsed_data = extractor.extract(text, lines)
                
            parsed_data['filename'] = filename
            
            # Save to DB
            invoice_id = InvoiceModel.insert_invoice(parsed_data)
            flash('Invoice processed successfully!', 'success')
            
            return render_template('result.html', data=parsed_data, id=invoice_id)
        else:
            flash('Allowed file types are png, jpg, jpeg, pdf', 'danger')
            return redirect(request.url)
            
    return render_template('upload.html')

@app.route('/invoices')
def invoices():
    all_invoices = InvoiceModel.get_all_invoices()
    return render_template('invoices.html', invoices=all_invoices)

@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('q', '')
    results = []
    if query:
        results = InvoiceModel.search_invoices(query)
    return render_template('search.html', query=query, results=results)

@app.route('/export/csv')
def export_csv():
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'export.csv')
    export_invoices_to_csv(output_path)
    return send_file(output_path, as_attachment=True)

@app.route('/export/pdf')
def export_pdf():
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'export.pdf')
    export_invoices_to_pdf(output_path)
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
