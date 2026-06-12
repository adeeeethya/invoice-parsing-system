import mysql.connector
import os

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "root"
DB_NAME = "invoice_db"

def get_db_connection():
    """Returns a connection to the MySQL database."""
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    return conn

def init_db():
    """Initializes the database and creates the invoices table if it doesn't exist."""
    # First, connect without database to create it if not exists
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    cursor.close()
    conn.close()

    # Now connect to the new database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Drop old tables to apply new schema (order matters for foreign key constraint)
    cursor.execute('DROP TABLE IF EXISTS invoice_items')
    cursor.execute('DROP TABLE IF EXISTS invoices')
    
    # Create new table structure
    cursor.execute('''
        CREATE TABLE invoices (
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
        )
    ''')
    
    # Create new table structure for invoice items
    cursor.execute('''
        CREATE TABLE invoice_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            invoice_id INT,
            description TEXT,
            quantity FLOAT,
            unit_price FLOAT,
            total_price FLOAT,
            FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("MySQL Database initialized successfully.")
