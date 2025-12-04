from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Product:
    """Represents a single product in the inventory."""
    name: str
    price: float
    quantity: int
    category: str


class Inventory:
    """Manages a collection of products and basic inventory operations."""

    def __init__(self, filename: str = "inventory.csv", low_stock_threshold: int = 5) -> None:
        """
        :param filename: Path to the CSV file used for persistence.
        :param low_stock_threshold: Quantity at or below which an item is considered low stock.
        """
        self.filename = filename
        self.low_stock_threshold = low_stock_threshold
        self.products: List[Product] = []

    def add_product(self, product: Product) -> None:
        """Add a new product if its name is unique (case-insensitive)."""
        if any(p.name.lower() == product.name.lower() for p in self.products):
            raise ValueError("Product already exists.")
        self.products.append(product)

    def update_product(
        self,
        name: str,
        new_price: Optional[float] = None,
        new_quantity: Optional[int] = None,
        new_category: Optional[str] = None,
    ) -> None:
        """
        Update price, quantity and/or category for the given product.

        :param name: Name of the product to update.
        :param new_price: New price (if any).
        :param new_quantity: New quantity (if any).
        :param new_category: New category (if any).
        """
        for product in self.products:
            if product.name.lower() == name.lower():
                if new_price is not None:
                    product.price = new_price
                if new_quantity is not None:
                    product.quantity = new_quantity
                if new_category is not None:
                    product.category = new_category
                return
        raise ValueError("Product not found.")

    def delete_product(self, name: str) -> None:
        """Delete a product by name (case-insensitive)."""
        original_len = len(self.products)
        self.products = [p for p in self.products if p.name.lower() != name.lower()]
        if len(self.products) == original_len:
            raise ValueError("Product not found.")

    def search_product(self, keyword: str) -> List[Product]:
        """Return all products where the keyword appears in the name or category."""
        keyword = keyword.lower().strip()
        return [
            p for p in self.products
            if keyword in p.name.lower() or keyword in p.category.lower()
        ]

    def low_stock_items(self) -> List[Product]:
        """Return products whose quantity is at or below the low-stock threshold."""
        return [p for p in self.products if p.quantity <= self.low_stock_threshold]
