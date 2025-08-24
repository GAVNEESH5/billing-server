# ui/main_ui.py
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from utils.db_utils import connect_db, init_database
from utils.db_utils import save_order as db_save_order  # optional reuse
# Calculator is optional; per-item GST ke liye hum yahin compute kar rahe
# from utils.calculator import calculate_order_totals

class RestaurantBillingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Restaurant Billing Software")
        self.root.geometry("1000x700")

        # Initialize database (centralized, robust)
        init_database()

        # GUI
        self.create_widgets()

        # Load menu
        self.load_menu()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Order type
        order_type_frame = ttk.LabelFrame(main_frame, text="Order Type", padding="5")
        order_type_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.order_type = tk.StringVar(value="Dine-In")
        ttk.Radiobutton(order_type_frame, text="Dine-In", variable=self.order_type, value="Dine-In").grid(row=0, column=0, padx=5)
        ttk.Radiobutton(order_type_frame, text="Takeaway", variable=self.order_type, value="Takeaway").grid(row=0, column=1, padx=5)

        # Menu
        menu_frame = ttk.LabelFrame(main_frame, text="Menu Items", padding="5")
        menu_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        self.menu_listbox = tk.Listbox(menu_frame, height=12, width=32)
        self.menu_listbox.grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(menu_frame, text="Add to Order", command=self.add_to_order).grid(row=1, column=0, pady=5)

        # Order
        order_frame = ttk.LabelFrame(main_frame, text="Current Order", padding="5")
        order_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        self.order_tree = ttk.Treeview(order_frame, columns=("Item", "Qty", "Price", "Total"), show="headings", height=10)
        for c in ("Item", "Qty", "Price", "Total"):
            self.order_tree.heading(c, text=c)
        self.order_tree.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        ttk.Button(order_frame, text="Remove Item", command=self.remove_item).grid(row=1, column=0, pady=5)
        ttk.Button(order_frame, text="Clear Order", command=self.clear_order).grid(row=1, column=1, pady=5)

        # Payment
        payment_frame = ttk.LabelFrame(main_frame, text="Payment Details", padding="5")
        payment_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(payment_frame, text="Discount:").grid(row=0, column=0, padx=5)
        self.discount_var = tk.DoubleVar(value=0.0)
        discount_entry = ttk.Entry(payment_frame, textvariable=self.discount_var, width=10)
        discount_entry.grid(row=0, column=1, padx=5)
        discount_entry.bind("<KeyRelease>", lambda e: self.update_order_display())  # live update

        ttk.Label(payment_frame, text="Payment Method:").grid(row=0, column=2, padx=5)
        self.payment_method = tk.StringVar(value="Cash")
        ttk.Combobox(payment_frame, textvariable=self.payment_method, values=["Cash", "Card", "UPI"], width=10).grid(row=0, column=3, padx=5)

        # Totals
        total_frame = ttk.LabelFrame(main_frame, text="Order Summary", padding="5")
        total_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.subtotal_label = ttk.Label(total_frame, text="Subtotal: $0.00")
        self.subtotal_label.grid(row=0, column=0, padx=5)
        self.gst_label = ttk.Label(total_frame, text="GST: $0.00")
        self.gst_label.grid(row=0, column=1, padx=5)
        self.discount_label = ttk.Label(total_frame, text="Discount: $0.00")
        self.discount_label.grid(row=0, column=2, padx=5)
        self.total_label = ttk.Label(total_frame, text="Total: $0.00", font=('Arial', 12, 'bold'))
        self.total_label.grid(row=0, column=3, padx=5)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Generate Bill", command=self.generate_bill).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="View Reports", command=self.view_reports).grid(row=0, column=1, padx=5)

        # State
        self.current_order = []  # list of tuples: (item_name, quantity)
        self.menu_items = {}     # item_name -> {"price": x, "gst": y}

    def load_menu(self):
        conn = connect_db()
        cur = conn.cursor()
        try:
            # Ensure menu has data (if you prefer, call populate_sample_data() in db_utils)
            cur.execute("SELECT COUNT(*) FROM menu;")
            if cur.fetchone()[0] == 0:
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
                cur.executemany("INSERT INTO menu (item_name, category, price, gst) VALUES (?, ?, ?, ?);", sample_menu)
                conn.commit()

            # Load item_name, price, gst
            cur.execute("SELECT item_name, price, gst FROM menu ORDER BY item_name;")
            rows = cur.fetchall()
            for r in rows:
                name, price, gst = r["item_name"], r["price"], r["gst"]
                self.menu_listbox.insert(tk.END, f"{name} - ${price:.2f}")
                self.menu_items[name] = {"price": float(price), "gst": float(gst)}
        finally:
            conn.close()

    def add_to_order(self):
        sel = self.menu_listbox.curselection()
        if not sel:
            messagebox.showwarning("Warning", "Please select an item from the menu")
            return
        item_text = self.menu_listbox.get(sel[0])
        item_name = item_text.split(" - ")[0]

        # If exists, increment; else add
        for i, (name, qty) in enumerate(self.current_order):
            if name == item_name:
                self.current_order[i] = (name, qty + 1)
                break
        else:
            self.current_order.append((item_name, 1))

        self.update_order_display()

    def remove_item(self):
        sel = self.order_tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return
        idx = self.order_tree.index(sel[0])
        del self.current_order[idx]
        self.update_order_display()

    def clear_order(self):
        self.current_order = []
        self.update_order_display()

    def _compute_totals(self):
        """
        Per-item GST calculation.
        Returns: (subtotal, gst_total, discount, grand_total, line_items_for_db)
        """
        subtotal = 0.0
        gst_total = 0.0
        line_items = []  # (item_name, qty, unit_price)

        for item_name, qty in self.current_order:
            meta = self.menu_items.get(item_name, {"price": 0.0, "gst": 0.0})
            price = meta["price"]
            gst_rate = meta["gst"]  # percentage
            line_total = price * qty
            subtotal += line_total
            gst_total += line_total * (gst_rate / 100.0)
            line_items.append((item_name, qty, price))

        # Discount validation
        try:
            discount = float(self.discount_var.get() or 0.0)
        except Exception:
            discount = 0.0
        if discount < 0:
            discount = 0.0
        # Max discount = subtotal + gst_total
        max_disc = round(subtotal + gst_total, 2)
        if discount > max_disc:
            discount = max_disc

        grand_total = subtotal + gst_total - discount
        return (round(subtotal, 2), round(gst_total, 2), round(discount, 2), round(grand_total, 2), line_items)

    def update_order_display(self):
        # Clear rows
        for iid in self.order_tree.get_children():
            self.order_tree.delete(iid)

        # Fill rows
        for item_name, qty in self.current_order:
            price = self.menu_items[item_name]["price"]
            total = price * qty
            self.order_tree.insert("", "end", values=(item_name, qty, f"${price:.2f}", f"${total:.2f}"))

        subtotal, gst_total, discount, grand_total, _ = self._compute_totals()
        self.subtotal_label.config(text=f"Subtotal: ${subtotal:.2f}")
        self.gst_label.config(text=f"GST: ${gst_total:.2f}")
        self.discount_label.config(text=f"Discount: ${discount:.2f}")
        self.total_label.config(text=f"Total: ${grand_total:.2f}")

    def generate_bill(self):
        if not self.current_order:
            messagebox.showwarning("Warning", "No items in order")
            return

        subtotal, gst_total, discount, grand_total, line_items = self._compute_totals()

        # Save to DB (reuse helper)
        order_id = db_save_order(
            order_type=self.order_type.get(),
            subtotal=subtotal,
            gst=gst_total,
            discount=discount,
            total=grand_total,
            payment_method=self.payment_method.get(),
            items=line_items
        )

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bill_lines = [
            f"Order #{order_id}",
            f"Type: {self.order_type.get()}",
            f"Date: {now}",
            "",
            "Items:"
        ]
        for (name, qty, price) in line_items:
            bill_lines.append(f"{name} x{qty} @ ${price:.2f} = ${price*qty:.2f}")
        bill_lines += [
            f"",
            f"Subtotal: ${subtotal:.2f}",
            f"GST: ${gst_total:.2f}",
            f"Discount: ${discount:.2f}",
            f"Total: ${grand_total:.2f}",
            f"Payment: {self.payment_method.get()}",
        ]
        messagebox.showinfo("Bill Generated", "\n".join(bill_lines))
        self.clear_order()

    def view_reports(self):
        conn = connect_db()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT DATE(order_date) AS date, SUM(total) AS sum_total, COUNT(*) AS cnt
                FROM orders
                GROUP BY DATE(order_date)
                ORDER BY date DESC
                LIMIT 7;
            """)
            rows = cur.fetchall()
        finally:
            conn.close()

        if not rows:
            messagebox.showinfo("Sales Report", "No orders yet.")
            return

        report_lines = ["Sales Report (Last 7 Days)", ""]
        for r in rows:
            report_lines.append(f"{r['date']}: ${float(r['sum_total']):.2f} ({r['cnt']} orders)")
        messagebox.showinfo("Sales Report", "\n".join(report_lines))
