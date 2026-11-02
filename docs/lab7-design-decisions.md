# Lab 7 Design Decisions

## Responsibilities

- **Keenan:** `routes/listprod.py` and `routes/listorder.py`.
- **Mathijs:** `routes/order.py` and presenting the completed lab.
- **Both:** Review and test the complete shopping process.

## Shared Code Decisions

- Keep the starter's project structure, database schema, routes, and appearance.
- Discuss changes to shared files before editing them.
- Use `get_connection()` from `db.py` and close connections in `finally`.
- Use parameterized SQL with `?` placeholders for input values.
- Keep the existing `session['productList']` cart format: `id`, `name`, `price`, and `quantity`.
- Generate add-to-cart links using the starter's Flask `url_for()` pattern.
- Use `escape_html()` for displayed text and `format_currency()` for money.
- Order listing uses prices saved in `orderproduct`, not current product prices. Later price changes must not change existing orders.

## Saving Orders

- Validate the customer ID and reject an empty cart before creating an order.
- Use product IDs and quantities from the cart. Retrieve current product names and prices from the database when saving the order.
- Check that every product exists and each quantity is a positive integer. Reject the whole order if any item is invalid and preserve the cart.
- If database prices differ from the prices shown in the cart, display the updated prices and total and ask the customer to confirm before saving. Recheck prices when confirmation is submitted.
- Use decimal arithmetic for money. Calculate each line total as `price * quantity` and sum the line totals for the order total.
- Save the order, its items, the unit prices used, and its total in one transaction.
- Commit only after all database changes succeed. Roll back on failure.
- Clear the cart only after a successful commit.
- Display confirmation using the saved order details and prices.
- Show a clear error message when checkout fails and preserve the cart.
