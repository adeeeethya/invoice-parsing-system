from database.db import get_db_connection

class InvoiceModel:
    @staticmethod
    def insert_invoice(data):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Using INSERT IGNORE to prevent duplicate invoice numbers if they exist
        cursor.execute('''
            INSERT IGNORE INTO invoices (
                vendor_name, invoice_number, invoice_date, tax_number, currency, 
                subtotal, gst_amount, cgst, sgst, igst, grand_total, filename, raw_ocr_text
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            data.get('vendor_name', ''),
            data.get('invoice_number', ''),
            data.get('invoice_date', ''),
            data.get('tax_number', ''),
            data.get('currency', ''),
            data.get('subtotal', 0.0),
            data.get('gst_amount', 0.0),
            data.get('cgst', 0.0),
            data.get('sgst', 0.0),
            data.get('igst', 0.0),
            data.get('grand_total', 0.0),
            data.get('filename', ''),
            data.get('raw_ocr_text', '')
        ))
        
        invoice_id = cursor.lastrowid
        
        # If insertion was ignored due to duplicate invoice_number, find the existing row ID
        if invoice_id == 0 or invoice_id is None:
            inv_num = data.get('invoice_number', '')
            if inv_num:
                cursor.execute('SELECT id FROM invoices WHERE invoice_number = %s', (inv_num,))
                row = cursor.fetchone()
                if row:
                    invoice_id = row[0]
        
        # Insert or update line items
        if invoice_id:
            # Delete existing line items for duplicate re-processing
            cursor.execute('DELETE FROM invoice_items WHERE invoice_id = %s', (invoice_id,))
            
            line_items = data.get('line_items', [])
            for item in line_items:
                cursor.execute('''
                    INSERT INTO invoice_items (invoice_id, description, quantity, unit_price, total_price)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (
                    invoice_id,
                    item.get('description', ''),
                    item.get('quantity', 1.0),
                    item.get('unit_price', 0.0),
                    item.get('total_price', 0.0)
                ))
        
        conn.commit()
        cursor.close()
        conn.close()
        return invoice_id

    @staticmethod
    def get_all_invoices():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM invoices ORDER BY id DESC')
        invoices = cursor.fetchall()
        
        for inv in invoices:
            cursor.execute('SELECT * FROM invoice_items WHERE invoice_id = %s ORDER BY id ASC', (inv['id'],))
            inv['line_items'] = cursor.fetchall()
            
        cursor.close()
        conn.close()
        return invoices

    @staticmethod
    def get_recent_invoices(limit=5):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM invoices ORDER BY id DESC LIMIT %s', (limit,))
        invoices = cursor.fetchall()
        
        for inv in invoices:
            cursor.execute('SELECT * FROM invoice_items WHERE invoice_id = %s ORDER BY id ASC', (inv['id'],))
            inv['line_items'] = cursor.fetchall()
            
        cursor.close()
        conn.close()
        return invoices

    @staticmethod
    def search_invoices(query):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        search_term = f'%{query}%'
        cursor.execute('''
            SELECT * FROM invoices 
            WHERE invoice_number LIKE %s 
               OR vendor_name LIKE %s 
               OR invoice_date LIKE %s
            ORDER BY id DESC
        ''', (search_term, search_term, search_term))
        invoices = cursor.fetchall()
        
        for inv in invoices:
            cursor.execute('SELECT * FROM invoice_items WHERE invoice_id = %s ORDER BY id ASC', (inv['id'],))
            inv['line_items'] = cursor.fetchall()
            
        cursor.close()
        conn.close()
        return invoices

    @staticmethod
    def get_invoice_items(invoice_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM invoice_items WHERE invoice_id = %s ORDER BY id ASC', (invoice_id,))
        items = cursor.fetchall()
        cursor.close()
        conn.close()
        return items

    @staticmethod
    def get_statistics():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Total number of invoices
        cursor.execute('SELECT COUNT(*) AS count FROM invoices')
        total_invoices = cursor.fetchone()['count']
        
        # Total amount spent
        cursor.execute('SELECT SUM(grand_total) AS total FROM invoices')
        total_amount = cursor.fetchone()['total'] or 0.0
        
        # Monthly statistics (MySQL SUBSTRING)
        cursor.execute('''
            SELECT SUBSTRING(created_at, 1, 7) as month, SUM(grand_total) as total
            FROM invoices
            GROUP BY month
            ORDER BY month ASC
        ''')
        monthly_stats_raw = cursor.fetchall()
        
        monthly_stats = {
            'labels': [row['month'] for row in monthly_stats_raw],
            'data': [row['total'] for row in monthly_stats_raw]
        }
        
        cursor.close()
        conn.close()
        return {
            'total_invoices': total_invoices,
            'total_amount': total_amount,
            'monthly_stats': monthly_stats
        }
