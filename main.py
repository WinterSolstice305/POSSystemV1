#!/usr/bin/env python3

"""Mini shopping cart POS application."""

from __future__ import annotations

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
	sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import modifyProductList
import modifyShoppingCart
import otherUtils

# Constants
XSIZE = 120
XSIZE2 = XSIZE // 2
XSIZE3 = XSIZE // 3
XSIZE4 = XSIZE // 4
FILL1 = "-"
FILL2 = "="
SALES_REPORT_FILE = Path(__file__).with_name("salesReport.json")


def main() -> None:
	while True:
		title_bar("PERFUME STORE", XSIZE, FILL1)
		print(
			"Available Actions\n",
			"[B] Browse products\n",
			"[V] View and Checkout or Modify cart\n",
			"[P] Update product stock \n",
			"[H] Show the Help manual for this system\n",
			"[S] Show Current Sales Report\n",
			"[Q] Quit this system.\n",
			"-" * XSIZE,
		)
		user_answer = otherUtils.ansCage(["B", "V", "P", "H", "S", "Q"], "Choice?: ", 0)
		match user_answer:
			case "B":
				display_products()
			case "V":
				checkout_cart()
			case "P":
				update_stock()
			case "H":
				display_help()
			case "S":
				showSalesReport()
			case "Q":
				print("Exiting....")
				sys.exit()
			case _:
				print("Invalid Value. Please choose from the choices given")


def display_help() -> None:
	help_path = Path(__file__).with_name("help_me.txt")
	if help_path.exists():
		text = help_path.read_text(encoding="utf-8")
	else:
		text = "Help file not found. Please contact the administrator."
	print(f"\n{text}\n")


def display_products() -> None:
	product_list = modifyProductList.load_products()

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
				item_quantity = int(otherUtils.ansCage([], "How many will you add?", 1))
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

	current_quantity = int(relevant_item.get("Stock", 0))
	new_quantity = int(otherUtils.ansCage([current_quantity], "Change to Quantity: ", 3))

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

	title_bar("RECEIPT", XSIZE, FILL2)
	print(f"{'Item':<{XSIZE3}} {'Qty.':<{XSIZE3}} {'Cost':>{XSIZE3}}")

	subtotal_prices = []
	for item in shopping_cart:
		unit_cost = float(item["Price"])
		quantity = int(item["Stock"])
		total_cost = unit_cost * quantity
		print(f"{item['Name']:<{XSIZE3}} x{quantity:<{XSIZE3}} ₱{total_cost:.2f}")
		subtotal_prices.append(total_cost)
	print("".center(XSIZE, FILL1))

	subtotal = calculate_subtotal(subtotal_prices)
	discount_list = [
		{"Name": "Above ₱100 Discount", "Discount%": 0.10, "Condition": int(subtotal >= 100)},
		{"Name": "Senior/PWD/Student Discount", "Discount%": 0.20, "Condition": 0},
	]

	if otherUtils.ansCage(["Y", "N"], "Senior/PWD/Student discount?", 0) == "Y":
		discount_list[1]["Condition"] = 1

	print(f"{'Subtotal':<{XSIZE2}} ₱{subtotal:.2f}")
	total_discount = calculate_discount(discount_list, subtotal)
	total_total = calculate_total(subtotal, total_discount)
	print(f"{'TOTAL':<{XSIZE2}} ₱{total_total:.2f}")

	change = calculate_change(total_total)
	print(f"{'Change:':<{XSIZE2}} ₱{change:.2f}")

	try:
		updated_products = modifyProductList.update_products_from_cart(product_list, shopping_cart)
		modifyProductList.save_products(updated_products)
	except ValueError as error:
		print(f"ERROR! {error}")
		print("Checkout cancelled....")
		return

	sales_report = _load_sales_report()
	sales_report.append(
		{
			"Total Items Sold": sum(int(item["Stock"]) for item in shopping_cart),
			"Gross Sales": subtotal,
			"Total Discounts": total_discount,
			"Net Sales": total_total,
		}
	)
	_save_sales_report(sales_report)

	modifyShoppingCart.empty_cart()
	print("Thank you for your patronage!")
	
def update_stock() -> None:
	while True:
		product_list = modifyProductList.load_products()
		title_bar("UPDATE STOCK", XSIZE, FILL1)

		if not product_list:
			print("There are no products in the catalog.")
		else:
			print(f"{'Item Code':<{XSIZE4}} {'Name':<{XSIZE4}} {'Price':<{XSIZE4}} {'Stock':<{XSIZE4}}")
			for item in product_list:
				print(f"{item['Code']:<{XSIZE4}} {item['Name']:<{XSIZE4}} ₱{item['Price']:<{XSIZE4}} {item['Stock']:<{XSIZE4}}")

		print("".center(XSIZE, FILL1))
		print(
			"Available Actions:\n",
			"[E] Edit product stock\n",
			"[A] Add product\n",
			"[R] Remove product\n",
			"[Q] Go back\n",
		)

		user_choice = otherUtils.ansCage(["E", "A", "R", "Q"], "Choice: ", 0)
		match user_choice:
			case "E":
				if not product_list:
					print("Error! There are no products to update.")
					continue

				item_code = otherUtils.ansCage(modifyProductList.get_product_codes(product_list), "Product Code", 2)
				product = modifyProductList.find_product(product_list, item_code)
				if product is None:
					print("Product not found.")
					continue

				while True:
					try:
						new_stock = int(float(otherUtils.ansCage([], "New stock quantity: ", 1)))
						if new_stock < 0:
							raise ValueError
						break
					except ValueError:
						print("Stock must be a non-negative number.")

				product["Stock"] = new_stock
				modifyProductList.save_products(product_list)
				print("Product stock updated!")
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

				while True:
					try:
						price = int(float(otherUtils.ansCage([], "Price: ", 1)))
						if price < 0:
							raise ValueError
						break
					except ValueError:
						print("Price must be a non-negative number.")

				while True:
					try:
						stock = int(float(otherUtils.ansCage([], "Stock: ", 1)))
						if stock < 0:
							raise ValueError
						break
					except ValueError:
						print("Stock must be a non-negative number.")

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
				print("Product removed successfully!")
			case "Q":
				return
			case _:
				print("Invalid Value!")


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


def calculate_change(total):
	while True:
		payment = float(otherUtils.ansCage([], "Enter Payment", 1))
		change = payment - total
		if change < 0:
			print("Insufficient Payment!!!")
			continue
		return change


def update_list_of_products(list_of_products, shopping_cart):
	try:
		return modifyProductList.update_products_from_cart(list_of_products, shopping_cart)
	except ValueError:
		return 0


if __name__ == '__main__':
	main()
	sys.exit()