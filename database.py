import sqlite3

def create_table():
    conn = sqlite3.connect("prawn_accounts.db")
    cursor = conn.cursor()
    
    # Create table with correct column names matching operations.py
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        sno INTEGER PRIMARY KEY,
        date TEXT,
        time TEXT,
        customer_name TEXT,     -- Changed from 'customer' to 'customer_name'
        item TEXT,
        count INTEGER,
        quantity REAL,
        rate REAL,
        total REAL,
        advance_paid REAL,
        amount REAL,
        phone TEXT,
        location TEXT,
        payment_status TEXT     -- Ensure this exists
    )
    """)
    
    conn.commit()
    conn.close()