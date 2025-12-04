import sys
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

from inventory_logic import Product, Inventory
from file_handler import load_inventory, save_inventory


class IMSApp:
    """Main class for the Inventory Management System GUI."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("700x650")
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(False, False)

        # Inventory and state
        self.inventory = Inventory()
        self.inventory.products = load_inventory()

        # UI widgets
        self.name_entry: tk.Entry | None = None
        self.price_entry: tk.Entry | None = None
        self.quantity_entry: tk.Entry | None = None
        self.category_entry: tk.Entry | None = None
        self.search_entry: tk.Entry | None = None
        self.table: ttk.Treeview | None = None
        self.low_stock_label: tk.Label | None = None

        self.create_widgets()
        self.refresh_table()
        self.update_low_stock_label()

    # ----------------- UI SETUP -----------------

    def create_widgets(self) -> None:
        # Title
        title = tk.Label(
            self.root,
            text="Inventory Management System",
            font=("Helvetica", 18, "bold"),
            bg="#f0f0f0",
            pady=20,
        )
        title.pack()

        # Product form
        form_frame = tk.Frame(self.root, bg="#f0f0f0", pady=10)
        form_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(form_frame, text="Product Name:", bg="#f0f0f0").grid(
            row=0, column=0, sticky="w", pady=5
        )
        self.name_entry = tk.Entry(form_frame, width=35)
        self.name_entry.grid(row=0, column=1, pady=5, sticky="w")

        tk.Label(form_frame, text="Price (USD):", bg="#f0f0f0").grid(
            row=1, column=0, sticky="w", pady=5
        )
        self.price_entry = tk.Entry(form_frame, width=35)
        self.price_entry.grid(row=1, column=1, pady=5, sticky="w")

        tk.Label(form_frame, text="Quantity:", bg="#f0f0f0").grid(
            row=2, column=0, sticky="w", pady=5
        )
        self.quantity_entry = tk.Entry(form_frame, width=35)
        self.quantity_entry.grid(row=2, column=1, pady=5, sticky="w")

        tk.Label(form_frame, text="Category:", bg="#f0f0f0").grid(
            row=3, column=0, sticky="w", pady=5
        )
        self.category_entry = tk.Entry(form_frame, width=35)
        self.category_entry.grid(row=3, column=1, pady=5, sticky="w")

        # Action buttons (Add / Update / Delete)
        button_frame = tk.Frame(self.root, bg="#f0f0f0", pady=10)
        button_frame.pack(pady=(0, 5))

        tk.Button(
            button_frame,
            text="Add Product",
            command=self.add_product,
            width=15,
            bg="#4CAF50",
            fg="white",
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            button_frame,
            text="Update Product",
            command=self.update_product,
            width=15,
            bg="#2196F3",
            fg="white",
        ).grid(row=0, column=1, padx=10)

        tk.Button(
            button_frame,
            text="Delete Product",
            command=self.delete_product,
            width=15,
            bg="#f44336",
            fg="white",
        ).grid(row=0, column=2, padx=10)

        # Search bar
        search_frame = tk.Frame(self.root, bg="#f0f0f0", pady=5)
        search_frame.pack(pady=(0, 5), padx=20, fill="x")

        tk.Label(search_frame, text="Search (name/category):", bg="#f0f0f0").grid(
            row=0, column=0, sticky="w", pady=5
        )
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.grid(row=0, column=1, pady=5, padx=(5, 5), sticky="w")

        tk.Button(
            search_frame,
            text="Search",
            command=self.search_product,
            width=12,
            bg="#03A9F4",
            fg="white",
        ).grid(row=0, column=2, padx=5)

        tk.Button(
            search_frame,
            text="Clear",
            command=self.clear_search,
            width=8,
            bg="#9E9E9E",
            fg="white",
        ).grid(row=0, column=3, padx=5)

        # Inventory table
        table_frame = tk.Frame(self.root, bg="#f0f0f0")
        table_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.table = ttk.Treeview(
            table_frame,
            columns=("Name", "Price (USD)", "Quantity", "Category"),
            show="headings",
            height=12,
        )
        for col in self.table["columns"]:
            self.table.heading(col, text=col)
            self.table.column(col, width=150, anchor="center")

        self.table.pack(side="left", expand=True, fill="both")

        # Scrollbar for table
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Double-click row to populate form
        self.table.bind("<Double-1>", self.on_row_double_click)

        # Low stock banner
        self.low_stock_label = tk.Label(
            self.root,
            text="",
            fg="red",
            bg="#f0f0f0",
            font=("Helvetica", 9, "bold"),
        )
        self.low_stock_label.pack(pady=(0, 10))

        # Bottom buttons (Generate report / Exit)
        action_frame = tk.Frame(self.root, bg="#f0f0f0", pady=10)
        action_frame.pack()

        tk.Button(
            action_frame,
            text="Generate Report",
            command=self.generate_report,
            width=18,
            bg="#FF9800",
            fg="white",
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            action_frame,
            text="Exit",
            command=self.exit_program,
            width=18,
            bg="#607D8B",
            fg="white",
        ).grid(row=0, column=1, padx=10)

    # ----------------- HELPER METHODS -----------------

    def _get_form_data(self) -> tuple[str, float, int, str]:
        """Validate and return the form data."""
        name = self.name_entry.get().strip()
        price_text = self.price_entry.get().strip()
        quantity_text = self.quantity_entry.get().strip()
        category = self.category_entry.get().strip()

        if not name or not price_text or not quantity_text or not category:
            raise ValueError("All fields must be filled.")

        try:
            price = float(price_text)
        except ValueError:
            raise ValueError("Price must be a valid number.")

        try:
            quantity = int(quantity_text)
        except ValueError:
            raise ValueError("Quantity must be a whole number.")

        return name, price, quantity, category

    def refresh_table(self, products=None) -> None:
        """Refresh the main table with all products or a given subset."""
        if self.table is None:
            return

        for row in self.table.get_children():
            self.table.delete(row)

        data = products if products is not None else self.inventory.products
        for p in data:
            self.table.insert(
                "",
                "end",
                values=(p.name, f"{p.price:.2f}", p.quantity, p.category),
            )

    def update_low_stock_label(self) -> None:
        """Update the low-stock banner at the bottom."""
        low_items = self.inventory.low_stock_items()
        if low_items and self.low_stock_label is not None:
            names = ", ".join(p.name for p in low_items)
            self.low_stock_label.config(
                text=f"Low stock: {names} (≤ {self.inventory.low_stock_threshold})"
            )
        elif self.low_stock_label is not None:
            self.low_stock_label.config(text="")

    def check_low_stock(self) -> None:
        """Backward-compatible wrapper for older calls."""
        self.update_low_stock_label()

    def clear_form(self) -> None:
        """Clear all input fields in the form."""
        self.name_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)

    def clear_search(self) -> None:
        """Clear search field and show all products."""
        if self.search_entry is not None:
            self.search_entry.delete(0, tk.END)
        self.refresh_table()

    # ----------------- EVENT HANDLERS -----------------

    def add_product(self) -> None:
        try:
            name, price, quantity, category = self._get_form_data()
            product = Product(name, price, quantity, category)
            self.inventory.add_product(product)
            save_inventory(self.inventory.products)
            self.refresh_table()
            self.update_low_stock_label()
            messagebox.showinfo("Success", f"{name} added to inventory.")
            self.clear_form()
        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))

    def update_product(self) -> None:
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Product name is required to update.")
            return

        price_text = self.price_entry.get().strip()
        quantity_text = self.quantity_entry.get().strip()
        category_text = self.category_entry.get().strip()

        new_price = None
        new_quantity = None
        new_category = None

        if price_text:
            try:
                new_price = float(price_text)
            except ValueError:
                messagebox.showerror("Input Error", "Price must be a valid number.")
                return

        if quantity_text:
            try:
                new_quantity = int(quantity_text)
            except ValueError:
                messagebox.showerror("Input Error", "Quantity must be a whole number.")
                return

        if category_text:
            new_category = category_text

        try:
            self.inventory.update_product(
                name,
                new_price=new_price,
                new_quantity=new_quantity,
                new_category=new_category,
            )
            save_inventory(self.inventory.products)
            self.refresh_table()
            self.update_low_stock_label()
            messagebox.showinfo("Success", f"{name} updated.")
            self.clear_form()
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))

    def delete_product(self) -> None:
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Product name is required to delete.")
            return

        try:
            self.inventory.delete_product(name)
            save_inventory(self.inventory.products)
            self.refresh_table()
            self.update_low_stock_label()
            messagebox.showinfo("Deleted", f"{name} removed from inventory.")
            self.clear_form()
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))

    def search_product(self) -> None:
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.refresh_table()
            return

        results = self.inventory.search_product(keyword)
        if not results:
            messagebox.showinfo("No Results", "No products found matching your search.")
        self.refresh_table(results)

    def generate_report(self) -> None:
        """Save current inventory and show confirmation with timestamp."""
        save_inventory(self.inventory.products)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        messagebox.showinfo(
            "Report Generated",
            f"Inventory report saved as inventory.csv\nGenerated at: {now}",
        )

    def on_row_double_click(self, event) -> None:
        """Populate the form when a row in the table is double-clicked."""
        selected = self.table.focus()
        if not selected:
            return
        values = self.table.item(selected, "values")
        if not values:
            return

        name, price, quantity, category = values
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, name)

        self.price_entry.delete(0, tk.END)
        self.price_entry.insert(0, price)

        self.quantity_entry.delete(0, tk.END)
        self.quantity_entry.insert(0, quantity)

        self.category_entry.delete(0, tk.END)
        self.category_entry.insert(0, category)

    def exit_program(self) -> None:
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.root.destroy()
            sys.exit()
