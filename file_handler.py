import csv
from typing import List
from inventory_logic import Product


def load_inventory(filename: str = "inventory.csv") -> List[Product]:
    """
    Load products from a CSV file into a list of Product instances.

    :param filename: CSV file path.
    :return: List of Product objects.
    """
    products: List[Product] = []

    try:
        with open(filename, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Expecting columns: Name, Price, Quantity, Category
                product = Product(
                    name=row["Name"],
                    price=float(row["Price"]),
                    quantity=int(row["Quantity"]),
                    category=row["Category"],
                )
                products.append(product)
    except FileNotFoundError:
        # Start with an empty list if file doesn't exist
        pass

    return products


def save_inventory(products: List[Product], filename: str = "inventory.csv") -> None:
    """
    Save a list of Product instances to a CSV file.

    :param products: List of Product objects to persist.
    :param filename: CSV file path.
    """
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        fieldnames = ["Name", "Price", "Quantity", "Category"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for product in products:
            writer.writerow(
                {
                    "Name": product.name,
                    "Price": product.price,
                    "Quantity": product.quantity,
                    "Category": product.category,
                }
            )
