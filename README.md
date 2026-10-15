# POS System v1

A command-line point-of-sale and inventory application. The program keeps its product catalog and active cart in JSON files located beside the Python modules.

## Capabilities

- Browse the catalog and add products to a persistent cart.
- Search products by a case-insensitive code or name.
- Edit cart quantities, remove cart items, and check out.
- Calculate a subtotal, one selected discount, payment, and change due.
- Decrease inventory after a successful checkout.
- Track and display sales report totals, with a function to reset the report.
- Add, edit, delete, view, search, and update stock for catalog products.
- Display the end-user help sheet from the main menu.
- Print a receipt with transaction number, date, item prices, payment, and change.

## Requirements and launch

- Python 3.10 or newer (the application uses structural pattern matching).
- No third-party packages are required.

Run from this directory:

```powershell
python .\main.py
```

The main menu accepts:

| Key | Action |
| --- | --- |
| `M` | Product management |
| `N` | Start a new transaction |
| `V` | View products |
| `S` | Search products by code or name |
| `R` | Show the current sales report |
| `C` | View or modify the cart, or check out |
| `H` | Show the help sheet |
| `Q` | Exit |

## Project layout

| File | Responsibility |
| --- | --- |
| `main.py` | CLI menus, display, input flow, checkout calculations, and user-facing catalog management. |
| `modifyProductList.py` | Product JSON persistence, numeric normalization, product lookup, and stock deduction for checkout. |
| `modifyShoppingCart.py` | Cart JSON persistence and cart operations (add, edit, remove, and clear). |
| `otherUtils.py` | Shared input prompts and validation modes. |
| `productsList.json` | Product catalog and on-hand stock. |
| `shoppingCart.json` | Current cart; persists between program runs. |
| `salesReport.json` | Completed checkout totals used to calculate the sales report. |
| `help_me.txt` | User-facing help text printed by the `H` action. Keep its menu keys in sync with `main.py`. |

## Data formats

The product catalog, shopping cart, and sales report are JSON arrays of objects. Keep each product's `Code` unique; cart operations and stock deduction use that code to find the matching catalog item.

### Product entry (`productsList.json`)

```json
{
  "Code": "BWB6",
  "Name": "Wheat Bread 600g",
  "Price": 90,
  "Stock": 997
}
```

Each successful checkout is stored in `salesReport.json` with its item count, gross sales (the subtotal), discounts, and net sales (the amount due after discount). The `R` main-menu action displays totals across all recorded checkouts and prompts for confirmation before clearing the report. Enter `Y` to reset it; any other response, including pressing Enter, leaves it unchanged.

`Code` and `Name` are strings. `Price` and `Stock` are integer values. Catalog-management prompts accept non-negative whole-number input and store it as an integer. Product codes entered through the add-product workflow are trimmed and uppercased.

### Cart entry (`shoppingCart.json`)

A cart entry has the same product fields as the catalog entry. Its `Stock` field represents the quantity in the cart, not the catalog's on-hand quantity. When a product is added, the cart stores a copy of its product data and the requested quantity.

## Main workflows

### Start a transaction and add products

Choose `N` from the main menu to start a transaction. `display_products()` shows the catalog and offers `A` (add to cart) or `Q` (finish browsing). Enter a product code and a positive whole-number quantity. The cart helper verifies that the product exists and that the requested quantity does not exceed available stock. Adding a product already in the cart merges the quantity. When browsing ends, the cart menu opens if the cart contains items.

Choose `V` from the main menu to view the catalog without adding products. Choose `S` to search by any part of a product code or name; matching is case-insensitive.

### Modify cart and check out

Choose `C` from the main menu to open the cart. `checkout_cart()` offers `C` (checkout), `E` (edit quantity), `R` (remove item), and `Q` (return). Edited quantities must be whole numbers from zero through the product's available stock; setting a quantity to zero removes the cart entry.

`display_receipt()` prints a transaction number, date, product, quantity, unit price, line amount, and subtotal. The customer selects one discount: none, student (10%), senior citizen (20%), or PWD (20%). The program requires payment at least equal to the total and displays the payment and change. It then deducts quantities from product stock, records the sale, and clears the cart. If a cart product is no longer in the catalog or stock is insufficient, checkout is cancelled.

Transaction numbers are based on the number of records in the sales report, so they can repeat after the report is reset.

### Manage the catalog

Choose `M` from the main menu for product management. `update_stock()` provides these actions:

- `A`: add a product with a name, unique code, price, and stock.
- `E`: edit a product's name or price.
- `U`: replace the stock quantity for an existing product.
- `R`: delete a product after confirmation.
- `V`: view products; `S`: search by code or name.
- `Q`: return to the main menu.

Catalog edits are saved through `modifyProductList.save_products()`. Stock and price must be non-negative whole numbers; a product name and code cannot be blank, and new product codes cannot duplicate existing codes.

## Design and extension guidance

- Keep terminal interaction and presentation in `main.py`; put reusable file and domain operations in the relevant helper module.
- Use `modifyProductList.load_products()` and `save_products()` for catalog access rather than reading or writing `productsList.json` directly. Use the corresponding `modifyShoppingCart` functions for cart access.
- Preserve the product field names and data types when extending the catalog. If a new field needs numeric normalization, update the product normalization logic as well as all consumers that display or use it.
- Keep cart quantity (`Stock` in the cart record) distinct from catalog stock. Checkout subtracts cart quantities from the catalog.
- Add or update tests for both the helper operation and the user-visible menu flow when introducing behavior. Test persistence using temporary data files or patched file paths so the checked-in JSON data is not changed.
- Update `help_me.txt` when user actions or menu shortcuts change, and update this README when module responsibilities, data formats, or workflows change.

## Persistence and current limitations

JSON files are the database. They are human-readable and simple to edit, but the application does not currently provide transactions, concurrent-user protection, schema migration, or automatic recovery from malformed JSON. Back up the data files before manual edits or experiments. The active cart is shared in one file rather than isolated per customer or session.
