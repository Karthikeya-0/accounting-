import sqlite3

# --- RESTORED TO ORIGINAL NAME ---
DB_NAME = "prawn_accounts.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create table with correct 14 columns
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        sno INTEGER PRIMARY KEY,
        date TEXT,
        time TEXT,
        customer_name TEXT,
        item TEXT,
        count INTEGER,TEXT,
        quantity REAL,
        rate REAL,
        total REAL,
        advance_paid REAL,
        amount REAL,
        phone TEXT,
        location TEXT,
        payment_status TEXT
    )
    """)
    conn.commit()
    conn.close()

def insert_record(values):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
    INSERT INTO accounts (
        sno, date, time, customer_name, item, count, 
        quantity, rate, total, advance_paid, amount, 
        phone, location, payment_status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(sql, values)
    conn.commit()
    conn.close()

def update_record(values):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
    UPDATE accounts SET
        date = ?,
        time = ?,
        customer_name = ?,
        item = ?,
        count = ?,
        quantity = ?,
        rate = ?,
        total = ?,
        advance_paid = ?,
        amount = ?,
        phone = ?,
        location = ?,
        payment_status = ?
    WHERE sno = ?
    """
    cursor.execute(sql, values)
    conn.commit()
    conn.close()

def delete_record(sno):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM accounts WHERE sno = ?", (sno,))
    conn.commit()
    conn.close()

def fetch_all():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accounts ORDER BY sno ASC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_by_sno(sno):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accounts WHERE sno = ?", (sno,))
    row = cursor.fetchone()
    conn.close()
    return row

def fetch_by_customer(name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accounts WHERE customer_name LIKE ?", ('%' + name + '%',))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_all_customer_names():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT customer_name FROM accounts ORDER BY customer_name ASC")
    names = [row[0] for row in cursor.fetchall()]
    conn.close()
    return names