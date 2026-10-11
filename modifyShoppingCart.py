"""Helpers for loading, editing, and clearing the shopping cart."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CART_FILE = Path(__file__).with_name("shoppingCart.json")


def load_cart() -> list[dict[str, Any]]:
    """Load the current cart from disk."""
    if not CART_FILE.exists():
        return []

    with CART_FILE.open("r", encoding="utf-8") as file:
        cart = json.load(file) or []

    normalized = []
    for item in cart:
        cleaned = dict(item)
        cleaned["Price"] = int(cleaned.get("Price", 0))
        cleaned["Stock"] = int(cleaned.get("Stock", 0))
        normalized.append(cleaned)
    return normalized


def save_cart(cart: list[dict[str, Any]]) -> None:
    """Persist the cart to disk."""
    with CART_FILE.open("w", encoding="utf-8") as file:
        json.dump(cart, file, indent="\t")


def get_cart_codes(cart: list[dict[str, Any]]) -> list[str]:
    """Return the list of item codes in the cart."""
    return [item["Code"] for item in cart]


def find_cart_item(cart: list[dict[str, Any]], item_code: str) -> dict[str, Any] | None:
    """Return the cart entry matching a product code."""
    for item in cart:
        if item.get("Code") == item_code:
            return item
    return None


def add_item_to_cart(product_list: list[dict[str, Any]], item_code: str, quantity: int) -> bool:
    """Add or merge a product into the cart while validating quantity."""
    quantity = int(quantity)
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

    product = next((item for item in product_list if item.get("Code") == item_code), None)
    if product is None:
        raise ValueError(f"Product code {item_code} does not exist.")

    available_stock = int(product.get("Stock", 0))
    current_cart_quantity = 0
    cart = load_cart()
    current_item = find_cart_item(cart, item_code)
    if current_item is not None:
        current_cart_quantity = int(current_item.get("Stock", 0))

    if current_cart_quantity + quantity > available_stock:
        raise ValueError("Requested quantity exceeds available stock.")

    if current_item is not None:
        current_item["Stock"] = current_cart_quantity + quantity
    else:
        new_entry = dict(product)
        new_entry["Stock"] = quantity
        cart.append(new_entry)

    save_cart(cart)
    return True


def edit_cart_item(item_code: str, new_quantity: int) -> None:
    """Update the quantity of a cart item."""
    new_quantity = int(new_quantity)
    if new_quantity < 0:
        raise ValueError("Quantity cannot be negative.")

    cart = load_cart()
    for item in cart:
        if item.get("Code") == item_code:
            if new_quantity == 0:
                cart.remove(item)
            else:
                item["Stock"] = new_quantity
            save_cart(cart)
            return

    raise ValueError(f"Item {item_code} is not in the cart.")


def remove_cart_item(item_code: str) -> None:
    """Remove one item from the cart by code."""
    cart = load_cart()
    for item in cart:
        if item.get("Code") == item_code:
            cart.remove(item)
            save_cart(cart)
            return

    raise ValueError(f"Item {item_code} is not in the cart.")


def empty_cart() -> None:
    """Clear the cart file."""
    save_cart([])
