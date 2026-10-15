"""Helpers for loading and updating the product catalog."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PRODUCTS_FILE = Path(__file__).with_name("productsList.json")


def load_products() -> list[dict[str, Any]]:
    """Load each product entry and normalize numeric fields."""
    if not PRODUCTS_FILE.exists():
        return []

    with PRODUCTS_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file) or []
    return normalize_numeric_fields(data)


def save_products(products: list[dict[str, Any]]) -> None:
    """Persist a product list to disk."""
    with PRODUCTS_FILE.open("w", encoding="utf-8") as file:
        json.dump(normalize_numeric_fields(products), file, indent="\t")


def normalize_numeric_fields(items: list[dict[str, Any]], fields: tuple[str, ...] = ("Price", "Stock")) -> list[dict[str, Any]]:
    """Cast known numeric fields to integers for consistent JSON usage."""
    normalized = []
    for item in items:
        cleaned = dict(item)
        for field in fields:
            if field in cleaned:
                cleaned[field] = int(cleaned[field])
        normalized.append(cleaned)
    return normalized


def get_product_codes(products: list[dict[str, Any]]) -> list[str]:
    """Return every product code in the catalog."""
    return [item["Code"] for item in products]


def find_product(products: list[dict[str, Any]], item_code: str) -> dict[str, Any] | None:
    """Return the relevant product record by code or None when missing."""
    for item in products:
        if item.get("Code") == item_code:
            return item
    return None


def update_products_from_cart(products: list[dict[str, Any]], cart: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Subtract every cart item from the stock in the product list."""
    product_map = {item["Code"]: item for item in products}
    for cart_item in cart:
        code = cart_item.get("Code")
        quantity = int(cart_item.get("Stock", 0))
        if code not in product_map:
            raise ValueError(f"Product {code} is no longer in the catalog.")

        product = product_map[code]
        product["Stock"] = int(product.get("Stock", 0)) - quantity
        if product["Stock"] < 0:
            raise ValueError(f"Insufficient stock for product {code}.")

    return products
