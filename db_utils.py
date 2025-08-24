# utils/db_utils.py
import sqlite3
import os
from datetime import datetime

# Resolve DB path relative to this file; ensure folder exists
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "db"))
os.makedirs(DB_DIR, exist_ok=True)

def connect_db(db_name="restaurant.db"):
    """
    Connect to SQLite DB with foreign keys enabled.
    Returns: sqlite3.Connection
    """
    db_path = os.path.join(DB_DIR, db_name)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_database():
    """Create tables if they don't exist."""
    conn = connect_db()
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS menu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL,
                price REAL NOT NULL CHECK(price > 0),
                gst REAL NOT NULL DEFAULT 5.0
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_type TEXT NOT NULL CHECK(order_type IN ('Dine-In', 'Takeaway')),
                subtotal REAL NOT NULL,
                gst REAL NOT NULL,
                discount REAL NOT NULL DEFAULT 0,
                total REAL NOT NULL,
                payment_method TEXT NOT NULL CHECK(payment_method IN ('Cash', 'Card', 'UPI')),
                order_date TEXT NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                price REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE
            );
        """)
        conn.commit()
    finally:
        conn.close()

def load_menu():
    """Return all menu rows ordered by category, item_name."""
    conn = connect_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM menu ORDER BY category, item_name;")
        return cur.fetchall()
    finally:
        conn.close()

def save_order(order_type, subtotal, gst, discount, total, payment_method, items):
    """
    Persist an order and its items atomically.
    items: list of tuples (item_name, quantity, price)
    Returns: order_id
    """
    conn = connect_db()
    try:
        cur = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""
            INSERT INTO orders (order_type, subtotal, gst, discount, total, payment_method, order_date)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (order_type, subtotal, gst, discount, total, payment_method, now))
        order_id = cur.lastrowid

        cur.executemany("""
            INSERT INTO order_items (order_id, item_name, quantity, price)
            VALUES (?, ?, ?, ?);
        """, [(order_id, n, q, p) for (n, q, p) in items])

        conn.commit()
        return order_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def get_orders_by_date(date_yyyy_mm_dd: str):
    """
    Return list of dicts: each order + its items.
    """
    conn = connect_db()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM orders
            WHERE DATE(order_date) = ?
            ORDER BY order_date DESC;
        """, (date_yyyy_mm_dd,))
        orders = cur.fetchall()

        result = []
        for row in orders:
            cur.execute("SELECT * FROM order_items WHERE order_id = ?;", (row["id"],))
            items = [dict(r) for r in cur.fetchall()]
            o = dict(row)
            o["items"] = items
            result.append(o)
        return result
    finally:
        conn.close()

def get_sales_summary(start_date, end_date):
    """
    Returns dict with 'daily_summary' and 'top_items'
    """
    conn = connect_db()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT DATE(order_date) AS date,
                   SUM(total) AS total_sales,
                   COUNT(*)  AS total_orders,
                   AVG(total) AS avg_order_value
            FROM orders
            WHERE DATE(order_date) BETWEEN ? AND ?
            GROUP BY DATE(order_date)
            ORDER BY date DESC;
        """, (start_date, end_date))
        daily_summary = cur.fetchall()

        cur.execute("""
            SELECT item_name, SUM(quantity) AS total_quantity
            FROM order_items
            WHERE order_id IN (
                SELECT id FROM orders
                WHERE DATE(order_date) BETWEEN ? AND ?
            )
            GROUP BY item_name
            ORDER BY total_quantity DESC
            LIMIT 5;
        """, (start_date, end_date))
        top_items = cur.fetchall()

        return {"daily_summary": daily_summary, "top_items": top_items}
    finally:
        conn.close()

def get_total_sales():
    conn = connect_db()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) AS total_orders,
                   SUM(total) AS total_sales,
                   AVG(total) AS avg_order_value
            FROM orders;
        """)
        r = cur.fetchone()
        return dict(r)
    finally:
        conn.close()

def populate_sample_data():
    """Insert default menu if empty."""
    conn = connect_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM menu;")
        if cur.fetchone()[0] > 0:
            return
        sample_menu = [
            ("Pizza", "Food", 10.00, 5),
            ("Burger", "Food", 5.00, 5),
            ("Coke", "Beverage", 2.00, 5),
            ("Salad", "Food", 4.00, 5),
            ("Pasta", "Food", 8.00, 5),
            ("Sandwich", "Food", 6.00, 5),
            ("Coffee", "Beverage", 3.00, 5),
            ("Tea", "Beverage", 2.50, 5),
            ("Ice Cream", "Dessert", 4.50, 5),
            ("Juice", "Beverage", 3.50, 5),
        ]
        cur.executemany(
            "INSERT INTO menu (item_name, category, price, gst) VALUES (?, ?, ?, ?);",
            sample_menu
        )
        conn.commit()
    finally:
        conn.close()
