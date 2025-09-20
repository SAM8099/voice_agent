import sqlite3
import datetime

def init_db():
    conn = sqlite3.connect("voice_agent.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS customers(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    phone TEXT,
                    email TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS complaints(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER,
                    description TEXT,
                    status TEXT,
                    created_at TEXT,
                    FOREIGN KEY(customer_id) REFERENCES customers(id))''')
    conn.commit()
    conn.close()
    
def book_complaint(customer_name, description):
    conn = sqlite3.connect("voice_agent.db")
    c = conn.cursor()
    customer_name = customer_name.lower()
    c.execute("SELECT id FROM customers WHERE name=?", (customer_name,))
    row = c.fetchone()
    if row:
        customer_id = row[0]
    else:
        c.execute("INSERT INTO customers (name) VALUES (?)", (customer_name,))
        conn.commit()
        customer_id = c.lastrowid

    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO complaints (customer_id, description, status, created_at) VALUES (?, ?, ?, ?)",
              (customer_id, description, "Open", created_at))
    conn.commit()
    complaint_id = c.lastrowid
    conn.close()
    return f"Complaint COMP-{complaint_id:03d} registered for {customer_name}"

def get_complaint_status(complaint_id):
    conn = sqlite3.connect("voice_agent.db")
    c = conn.cursor()
    try:
        cid = int(complaint_id.split("-")[1])
    except:
        return "Invalid complaint ID format. Please use COMP-###"
    c.execute("SELECT complaints.description, complaints.status, complaints.created_at, customers.name "
              "FROM complaints JOIN customers ON complaints.customer_id=customers.id "
              "WHERE complaints.id=?", (cid,))
    row = c.fetchone()
    conn.close()

    if row:
        desc, status, created, name = row
        return f"Complaint {complaint_id} for {name} about {desc} is currently {status} (filed on {created})"
    else:
        return f"I couldn't find complaint {complaint_id}. Please verify the complaint ID."

def get_customer_history(name):
    conn = sqlite3.connect("voice_agent.db")
    c = conn.cursor()
    name = name.lower()
    c.execute("SELECT id FROM customers WHERE name=?", (name,))
    row = c.fetchone()
    if not row:
        return f"No history found for {name}"

    customer_id = row[0]
    c.execute("SELECT id, description, status, created_at FROM complaints WHERE customer_id=?", (customer_id,))
    rows = c.fetchall()
    conn.close()
    if not rows:
        return f"No complaints found for {name}"

    history = [f"COMP-{rid:03d}: {desc}, Status: {status}, Date: {date}" for rid, desc, status, date in rows]
    return "\n".join(history)
