#!/usr/bin/env python3

"""Mini shopping cart POS application."""

from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
	sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import modifyProductList
import modifyShoppingCart
import otherUtils

# Constants
XSIZE = 90
XSIZE2 = XSIZE // 2
XSIZE3 = XSIZE // 3
XSIZE4 = XSIZE // 4
FILL1 = "-"
FILL2 = "="
SALES_REPORT_FILE = Path(__file__).with_name("salesReport.json")


@dataclass
class Transaction:
	items: list[dict[str, Any]]
	discount_name: str = "No Discount"
	discount_rate: float = 0.0
	payment: float = 0.0

	@property
	def subtotal(self) -> float:
		return calculate_subtotal(
			[float(item["Price"]) * int(item["Stock"]) for item in self.items]
		)

	@property
	def discount(self) -> float:
		return self.subtotal * self.discount_rate

	@property
	def total(self) -> float:
		return calculate_total(self.subtotal, self.discount)


def main() -> None:
	while True:
		title_bar("PERFUME STORE", XSIZE, FILL1)
		print(
			"Available Actions\n",
			"[M] Product Management\n",
			"[N] New Transaction\n",
			"[V] View Products\n",
			"[S] Search Product\n",
			"[R] Sales Report\n",
			"[Q] Exit\n",
			"[C] View or modify cart\n",
			"[H] Show the Help manual for this system\n",
			"-" * XSIZE,
		)
		user_answer = otherUtils.ansCage(
			["M", "N", "V", "S", "R", "Q", "C", "H"], "Choice?: ", 0
		)
		match user_answer:
			case "M":
				update_stock()
			case "N":
				display_products()
				if modifyShoppingCart.load_cart():
					checkout_cart()
			case "V":
				view_products()
			case "S":
				search_products()
			case "R":
				showSalesReport()
			case "Q":
				print("Exiting....")
				sys.exit()
			case "C":
				checkout_cart()
			case "H":
				display_help()


def view_products(products: list[dict[str, Any]] | None = None) -> None:
	if products is None:
		products = modifyProductList.load_products()
	title_bar("AVAILABLE PRODUCTS", XSIZE, FILL1)
	if not products:
		print("There are no products in the catalog.")
		return
	print(f"{'Item Code':<{XSIZE4}} {'Name':<{XSIZE4}} {'Price':<{XSIZE4}} {'Stock':<{XSIZE4}}")
	for item in products:
		print(f"{item['Code']:<{XSIZE4}} {item['Name']:<{XSIZE4}} ₱{item['Price']:<{XSIZE4}} {item['Stock']:<{XSIZE4}}")


def search_products() -> None:
	products = modifyProductList.load_products()
	query = input("Enter a product code or name to search: ").strip().casefold()
	if not query:
		print("Search text cannot be empty.")
		return
	matches = [
		item for item in products
		if query in str(item.get("Code", "")).casefold()
		or query in str(item.get("Name", "")).casefold()
	]
	if not matches:
		print("No matching products found.")
		return
	view_products(matches)


def display_help() -> None:
	help_path = Path(__file__).with_name("help_me.txt")
	if help_path.exists():
		text = help_path.read_text(encoding="utf-8")
	else:
		text = "Help file not found. Please contact the administrator."
	print(f"\n{text}\n")


def display_products() -> None:
	product_list = modifyProductList.load_products()
	if not product_list:
		print("There are no products in the catalog.")
		return

	while True:
		title_bar("AVAILABLE PRODUCTS", XSIZE, FILL1)
		print(f"{'Item Code':<{XSIZE4}} {'Name':<{XSIZE4}} {'Price':<{XSIZE4}} {'Stock':<{XSIZE4}}")

		product_codes = []
		for item in product_list:
			print(f"{item['Code']:<{XSIZE4}} {item['Name']:<{XSIZE4}} ₱{item['Price']:<{XSIZE4}} {item['Stock']:<{XSIZE4}}")
			product_codes.append(item["Code"])

		print("".center(XSIZE, FILL1))
		print("Available Actions:\n", "[A] Add to cart\n", "[Q] Go back\n")

		user_answer = otherUtils.ansCage(["A", "Q"], "Choice", 0)
		match user_answer:
			case "A":
				item_code = otherUtils.ansCage(product_codes, "Product Code", 2)
				item_quantity = prompt_nonnegative_integer("How many will you add?")
				add_to_cart(product_list, item_code, item_quantity)
			case "Q":
				break
			case _:
				print("Invalid Value. Please choose from the choices given")


def add_to_cart(list_of_products, item_code, item_quantity):
	try:
		modifyShoppingCart.add_item_to_cart(list_of_products, item_code, item_quantity)
		print("Item added to cart!")
	except ValueError as error:
		print(f"ERROR! {error}")


def checkout_cart() -> None:
	while True:
		shopping_cart = modifyShoppingCart.load_cart()
		title_bar("SHOPPING CART", XSIZE, FILL1)

		if not shopping_cart:
			print("Your shopping cart is empty.")
		else:
			print(f"{'Item Code':<{XSIZE4}} {'Name':<{XSIZE4}} {'Price':<{XSIZE4}} {'Stock':<{XSIZE4}}")
			for item in shopping_cart:
				print(f"{item['Code']:<{XSIZE4}} {item['Name']:<{XSIZE4}} ₱{item['Price']:<{XSIZE4}} {item['Stock']:<{XSIZE4}}")

		s_cart_codes = modifyShoppingCart.get_cart_codes(shopping_cart)
		print("".center(XSIZE, FILL1))
		print(
			"Available Actions:\n",
			"[C] Checkout cart\n",
			"[E] Edit quantity of an item\n",
			"[R] Remove an item\n",
			"[Q] Go back\n",
		)

		user_choice = otherUtils.ansCage(["C", "E", "R", "Q"], "Choice: ", 0)
		match user_choice:
			case "C":
				if not shopping_cart:
					print("Error! The cart is empty.")
					continue
				display_receipt()
				return
			case "E":
				if not s_cart_codes:
					print("Error! The cart has nothing to edit")
					continue
				edit_cart_item()
			case "R":
				if not s_cart_codes:
					print("Error! The cart has nothing to edit")
					continue
				remove_cart_item()
			case "Q":
				break
			case _:
				print("Invalid Value!")


def title_bar(text, width, fill_char):
	"""Print a simple decorative header."""
	print("\n\n\n")
	print("".center(width, fill_char))
	print(text.center(width))
	print("".center(width, fill_char))


def edit_cart_item():
	shopping_cart = modifyShoppingCart.load_cart()
	item_codes = modifyShoppingCart.get_cart_codes(shopping_cart)
	item_code = otherUtils.ansCage(item_codes, "Product Code", 2)

	relevant_item = modifyShoppingCart.find_cart_item(shopping_cart, item_code)
	if relevant_item is None:
		print("Item not found in cart.")
		return

	product = modifyProductList.find_product(modifyProductList.load_products(), item_code)
	if product is None:
		print("This product is no longer in the catalog. Remove it from the cart.")
		return

	available_stock = int(product.get("Stock", 0))
	new_quantity = int(otherUtils.ansCage([available_stock], "Change to Quantity: ", 3))

	try:
		modifyShoppingCart.edit_cart_item(item_code, new_quantity)
		print("Item quantity changed!")
	except ValueError as error:
		print(f"ERROR! {error}")


def remove_cart_item():
	shopping_cart = modifyShoppingCart.load_cart()
	item_codes = modifyShoppingCart.get_cart_codes(shopping_cart)
	item_code = otherUtils.ansCage(item_codes, "Product Code: ", 2)

	try:
		modifyShoppingCart.remove_cart_item(item_code)
		print("Item removed from cart!")
	except ValueError as error:
		print(f"ERROR! {error}")


def display_receipt():
	shopping_cart = modifyShoppingCart.load_cart()
	product_list = modifyProductList.load_products()
	if not shopping_cart:
		print("Error! The cart is empty.")
		return

	title_bar("RECEIPT", XSIZE, FILL2)
	transaction = Transaction(shopping_cart)
	try:
		updated_products = modifyProductList.update_products_from_cart(
			[dict(item) for item in product_list], shopping_cart
		)
	except ValueError as error:
		print(f"ERROR! {error}")
		print("Checkout cancelled....")
		return

	sales_report = _load_sales_report()
	print(f"Transaction No.: {len(sales_report) + 1:05d}")
	print(f"Date: {datetime.now():%m/%d/%Y}")
	print(f"{'Product':<{XSIZE3}} {'Qty.':>{XSIZE4}} {'Price':>{XSIZE4}} {'Amount':>{XSIZE4}}")
	for item in shopping_cart:
		unit_cost = float(item["Price"])
		quantity = int(item["Stock"])
		total_cost = unit_cost * quantity
		print(
			f"{item['Name']:<{XSIZE3}} {quantity:>{XSIZE4}} "
			f"₱{unit_cost:>{XSIZE4}.2f} ₱{total_cost:>{XSIZE4}.2f}"
		)
	print("".center(XSIZE, FILL1))

	discount_options = {
		"N": ("No Discount", 0.0),
		"S": ("Student Discount", 0.10),
		"C": ("Senior Citizen Discount", 0.20),
		"P": ("PWD Discount", 0.20),
	}
	print("Discount options: [N] No Discount, [S] Student (10%), [C] Senior Citizen (20%), [P] PWD (20%)")
	discount_choice = otherUtils.ansCage(list(discount_options), "Choose discount", 0)
	transaction.discount_name, transaction.discount_rate = discount_options[discount_choice]

	print(f"{'Subtotal':<{XSIZE2}} ₱{transaction.subtotal:.2f}")
	total_discount = transaction.discount
	print(f"{transaction.discount_name:<{XSIZE2}} ₱{total_discount:.2f}")
	total = transaction.total
	print(f"{'TOTAL':<{XSIZE2}} ₱{total:.2f}")

	transaction.payment = calculate_payment(total)
	change = transaction.payment - total
	print(f"{'Cash:':<{XSIZE2}} ₱{transaction.payment:.2f}")
	print(f"{'Change:':<{XSIZE2}} ₱{change:.2f}")

	modifyProductList.save_products(updated_products)

	sales_report.append(
		{
			"Total Items Sold": sum(int(item["Stock"]) for item in shopping_cart),
			"Gross Sales": transaction.subtotal,
			"Total Discounts": total_discount,
			"Net Sales": total,
		}
	)
	_save_sales_report(sales_report)

	modifyShoppingCart.empty_cart()
	print("Thank you for your patronage!")
	
def prompt_nonnegative_integer(prompt: str) -> int:
	while True:
		try:
			value = float(otherUtils.ansCage([], prompt, 1))
			if value < 0 or not value.is_integer():
				raise ValueError
			return int(value)
		except ValueError:
			print("Please enter a non-negative whole number.")


def update_stock() -> None:
	while True:
		product_list = modifyProductList.load_products()
		title_bar("PRODUCT MANAGEMENT", XSIZE, FILL1)
		view_products(product_list)
		print("".center(XSIZE, FILL1))
		print(
			"Available Actions:\n",
			"[A] Add product\n",
			"[E] Edit product name or price\n",
			"[U] Update product stock\n",
			"[R] Delete product\n",
			"[V] View products\n",
			"[S] Search products\n",
			"[Q] Go back\n",
		)

		user_choice = otherUtils.ansCage(["A", "E", "U", "R", "V", "S", "Q"], "Choice: ", 0)
		match user_choice:
			case "E" | "U":
				if not product_list:
					print("Error! There are no products to edit.")
					continue

				item_code = otherUtils.ansCage(modifyProductList.get_product_codes(product_list), "Product Code", 2)
				product = modifyProductList.find_product(product_list, item_code)
				if product is None:
					print("Product not found.")
					continue

				if user_choice == "U":
					product["Stock"] = prompt_nonnegative_integer("New stock quantity")
				else:
					field = otherUtils.ansCage(["N", "P", "Q"], "Edit [N]ame, [P]rice, or [Q]uit", 0)
					if field == "Q":
						continue
					if field == "N":
						new_name = input(f"Product name [{product['Name']}]: ").strip()
						if not new_name:
							print("Product name cannot be empty.")
							continue
						product["Name"] = new_name
					else:
						product["Price"] = prompt_nonnegative_integer("New price")
				modifyProductList.save_products(product_list)
				print("Product updated successfully!")
			case "A":
				product_name = input("Product Name: ").strip()
				if not product_name:
					print("Product name cannot be empty.")
					continue

				while True:
					product_code = input("Product Code: ").strip().upper()
					if not product_code:
						print("Product code cannot be empty.")
						continue
					if any(item.get("Code") == product_code for item in product_list):
						print("A product with this code already exists.")
						continue
					break

				price = prompt_nonnegative_integer("Price")
				stock = prompt_nonnegative_integer("Stock")

				product_list.append({
					"Name": product_name,
					"Price": price,
					"Stock": stock,
					"Code": product_code,
				})
				modifyProductList.save_products(product_list)
				print("Product added successfully!")
			case "R":
				if not product_list:
					print("Error! There are no products to remove.")
					continue

				item_code = otherUtils.ansCage(modifyProductList.get_product_codes(product_list), "Product Code: ", 2)
				product = modifyProductList.find_product(product_list, item_code)
				if product is None:
					print("Product not found.")
					continue

				confirmation = otherUtils.ansCage(["Y", "N"], f"Remove {product['Name']} ({item_code})?", 0)
				if confirmation == "N":
					print("Product removal cancelled.")
					continue

				product_list = [item for item in product_list if item.get("Code") != item_code]
				modifyProductList.save_products(product_list)
				print("Product deleted successfully!")
			case "V":
				view_products(product_list)
			case "S":
				search_products()
			case "Q":
				return


def showSalesReport() -> None:
	sales_report = _load_sales_report()
	total_items_sold = sum(int(transaction["Total Items Sold"]) for transaction in sales_report)
	gross_sales = sum(float(transaction["Gross Sales"]) for transaction in sales_report)
	total_discounts = sum(float(transaction["Total Discounts"]) for transaction in sales_report)
	net_sales = sum(float(transaction["Net Sales"]) for transaction in sales_report)

	title_bar("SALES REPORT", XSIZE, FILL1)
	print(f"{'Total Transactions':<{XSIZE2}} {len(sales_report)}")
	print(f"{'Total Items Sold':<{XSIZE2}} {total_items_sold}")
	print(f"{'Gross Sales':<{XSIZE2}} ₱{gross_sales:.2f}")
	print(f"{'Total Discounts':<{XSIZE2}} ₱{total_discounts:.2f}")
	print(f"{'Net Sales':<{XSIZE2}} ₱{net_sales:.2f}")

	reset_confirmation = input("Reset sales report? (Y/N) (default: N): ").strip().casefold()
	if reset_confirmation == "y":
		resetSalesReport()
		print("Sales report reset.")


def resetSalesReport() -> None:
	_save_sales_report([])


def _load_sales_report() -> list[dict[str, int | float]]:
	if not SALES_REPORT_FILE.exists():
		return []

	with SALES_REPORT_FILE.open("r", encoding="utf-8") as file:
		sales_report = json.load(file)
	if not isinstance(sales_report, list):
		raise ValueError("Sales report must contain a JSON array.")
	return sales_report


def _save_sales_report(sales_report: list[dict[str, int | float]]) -> None:
	with SALES_REPORT_FILE.open("w", encoding="utf-8") as file:
		json.dump(sales_report, file, indent="\t")


def calculate_subtotal(num_list):
	return sum(num_list)


def calculate_discount(discount_list: list, subtotal):
	total_discount = 0.0
	subtotal_copy = subtotal

	for item in discount_list:
		if item["Condition"] == 1:
			discount_amount = subtotal_copy * item["Discount%"]
			print(f"{item['Name']:<{XSIZE2}} ₱{discount_amount:.2f}")
			total_discount += discount_amount
			subtotal_copy -= discount_amount

	return total_discount


def calculate_total(subtotal, total_discount):
	return subtotal - total_discount


def calculate_payment(total):
	while True:
		try:
			payment = float(otherUtils.ansCage([], "Enter Payment", 1))
		except ValueError:
			continue
		if not math.isfinite(payment):
			print("Please enter a finite payment amount.")
			continue
		if payment < total:
			print("Insufficient Payment!!!")
			continue
		return payment


def calculate_change(total):
	return calculate_payment(total) - total


def update_list_of_products(list_of_products, shopping_cart):
	try:
		return modifyProductList.update_products_from_cart(list_of_products, shopping_cart)
	except ValueError:
		return 0


if __name__ == '__main__':
	main()
	sys.exit()