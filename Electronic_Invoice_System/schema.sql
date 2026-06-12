CREATE TABLE IF NOT EXISTS invoices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_name VARCHAR(255),
    invoice_number VARCHAR(255) UNIQUE,
    invoice_date VARCHAR(255),
    tax_number VARCHAR(255),
    currency VARCHAR(10),
    subtotal FLOAT,
    gst_amount FLOAT,
    cgst FLOAT,
    sgst FLOAT,
    igst FLOAT,
    grand_total FLOAT,
    filename VARCHAR(255),
    raw_ocr_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS invoice_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    invoice_id INT,
    description TEXT,
    quantity FLOAT,
    unit_price FLOAT,
    total_price FLOAT,
    FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
);
