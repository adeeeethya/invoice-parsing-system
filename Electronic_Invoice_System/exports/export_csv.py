import pandas as pd
from database.db import get_db_connection

def export_invoices_to_csv(output_path):
    """
    Exports all invoice records from the MySQL database to a CSV file.
    Returns the path to the generated CSV.
    """
    conn = get_db_connection()
    query = """
        SELECT 
            id AS `ID`, 
            invoice_number AS `Invoice No`, 
            invoice_date AS `Date`, 
            vendor_name AS `Vendor`, 
            tax_number AS `Tax/GST No`, 
            gst_amount AS `GST Amount`, 
            grand_total AS `Total Amount`, 
            filename AS `Filename` 
        FROM invoices 
        ORDER BY id DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    df.to_csv(output_path, index=False)
    return output_path
