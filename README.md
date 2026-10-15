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
| `1` | Product management |
| `2` | Start a new transaction |
| `3` | View products |
| `4` | Search products |
| `5` | Show the current sales report |
| `6` | Exit |
| `V` | View or modify the cart, or check out |
| `H` | Show the help sheet |

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

Both data files contain JSON arrays of objects. Keep each product's `Code` unique; cart operations and stock deduction use that code to find the matching catalog item.

### Product entry (`productsList.json`)

```json
{
  "Code": "BWB6",
  "Name": "Wheat Bread 600g",
  "Price": 90,
  "Stock": 997
}
```

Each successful checkout is stored in `salesReport.json` with its item count, gross sales, discounts, and net sales. The `5` main-menu action displays the totals across all recorded checkouts and prompts for confirmation before clearing the report. Enter `Y` to reset it; any other response, including pressing Enter, leaves it unchanged.

`Code` and `Name` are strings. `Price` and `Stock` are integer values. The current catalog-management prompts accept non-negative numeric input and store it as an integer. Product codes entered through the add-product workflow are trimmed and uppercased.

### Cart entry (`shoppingCart.json`)

A cart entry has the same product fields as the catalog entry. Its `Stock` field represents the quantity in the cart, not the catalog's on-hand quantity. When a product is added, the cart stores a copy of its product data and the requested quantity.

## Main workflows

### Browse and add to cart

`display_products()` loads the catalog and offers `A` (add) or `Q` (return). The cart helper verifies that the product exists and that the requested quantity is positive and does not exceed the catalog stock. Adding a product already in the cart merges the quantity.

### Modify cart and check out

`checkout_cart()` offers `C` (checkout), `E` (edit quantity), `R` (remove item), and `Q` (return). Setting an edited quantity to zero removes the cart entry.

`display_receipt()` calculates each line total and the subtotal. The customer selects one discount: none, student (10%), senior citizen (20%), or PWD (20%). The program requests payment, then deducts quantities from product stock and clears the cart after stock deduction succeeds.

### Manage the catalog

`update_stock()` provides the product-management menu:

- `A`: add a product with a name, unique code, price, and stock.
- `E`: edit a product's name or price.
- `U`: replace the stock quantity for an existing product.
- `R`: delete a product after confirmation.
- `V`: view products; `S`: search by code or name.
- `Q`: return to the main menu.

Catalog edits are saved through `modifyProductList.save_products()`. Stock and price must be non-negative; a product name and code cannot be blank, and new product codes cannot duplicate existing codes.

## Design and extension guidance

- Keep terminal interaction and presentation in `main.py`; put reusable file and domain operations in the relevant helper module.
- Use `modifyProductList.load_products()` and `save_products()` for catalog access rather than reading or writing `productsList.json` directly. Use the corresponding `modifyShoppingCart` functions for cart access.
- Preserve the product field names and data types when extending the catalog. If a new field needs numeric normalization, update the product normalization logic as well as all consumers that display or use it.
- Keep cart quantity (`Stock` in the cart record) distinct from catalog stock. Checkout subtracts cart quantities from the catalog.
- Add or update tests for both the helper operation and the user-visible menu flow when introducing behavior. Test persistence using temporary data files or patched file paths so the checked-in JSON data is not changed.
- Update `help_me.txt` when user actions or menu shortcuts change, and update this README when module responsibilities, data formats, or workflows change.

## Persistence and current limitations

JSON files are the database. They are human-readable and simple to edit, but the application does not currently provide transactions, concurrent-user protection, schema migration, or automatic recovery from malformed JSON. Back up the data files before manual edits or experiments. The active cart is shared in one file rather than isolated per customer or session.
