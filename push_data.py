import sqlite3
import datetime
from src.memory.database import init_db

init_db()
# Connect
conn = sqlite3.connect("voice_agent.db")
c = conn.cursor()

# Sample customers (names stored in lowercase)
customers = [
    ("alice smith", "9876543210", "alice@example.com"),
    ("bob johnson", "9123456780", "bob@example.com"),
    ("carol lee", "9988776655", "carol@example.com")
]

for name, phone, email in customers:
    c.execute("INSERT INTO customers (name, phone, email) VALUES (?, ?, ?)", (name, phone, email))

# Get customer IDs
c.execute("SELECT id, name FROM customers")
customer_map = {name: cid for cid, name in c.fetchall()}

# Sample complaints
complaints = [
    ("alice smith", "Internet not working", "Open", "2025-09-20 10:30:00"),
    ("alice smith", "Billing issue", "Closed", "2025-09-18 15:45:00"),
    ("bob johnson", "Slow internet speed", "Open", "2025-09-19 09:00:00"),
    ("carol lee", "Router not connecting to Wi-Fi", "Open", "2025-09-20 11:15:00"),
]

for name, desc, status, created_at in complaints:
    customer_id = customer_map[name]
    c.execute("INSERT INTO complaints (customer_id, description, status, created_at) VALUES (?, ?, ?, ?)",
              (customer_id, desc, status, created_at))

conn.commit()
conn.close()
print("Sample data inserted successfully!")