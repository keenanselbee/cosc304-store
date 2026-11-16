# Lab 8 Design Decisions

Build on the existing Python store with the required Lab 8 features and a simple cartoon fantasy theme. Keep the implementation small, readable and easy to maintain.

## Theme and Content

- The shop is **Gruk's Glorious Gear**, run by a cartoon orc merchant.
- Sell war axes, potions and equipment using **elf ears** as the displayed currency.
- Use [Lab 8 Shop Content](lab8-shop-content.md) for Gruk's personality, quotes, proposed products and image ideas. Item names and prices there remain a draft until implemented.
- Start with the proposed eight-item catalogue across Weapons, Armour and Potions. Map it onto existing product records without breaking order or inventory relationships.
- Keep the humour in descriptions and occasional fixed Gruk quotes. Use clear navigation labels and functional messages.
- Keep internal names such as `product`, `price`, `customer` and `inventory` straightforward.

## Appearance

- **Mockup A (Timber Shop) is the selected visual direction:** [shop mockup](../images/mockups/lab8-shop-mockup.png). Keep this reference in `images/mockups`.
- Use a simple layout with dark brown backgrounds, readable parchment-coloured panels, and green and gold accents.
- Keep one shared stylesheet and reuse the existing page-generation approach with a small shared header/menu where practical. Avoid a new frontend framework or a broad rewrite.
- Start with one static Gruk illustration and one cartoon image per themed product.
- Use familiar labels such as Shop, Cart, Checkout, My Account, Sales Report, Login and Logout.
- Keep tables, forms and text readable on smaller screens. Visual polish should not complicate the required behaviour.

## Frontend Implementation

- Use the selected mockup as a visual target, with small adjustments for readability and straightforward implementation.
- Reuse wood textures, the Gruk illustration and product pictures as image assets. Render headings, descriptions, prices, buttons and forms as real HTML rather than embedding the mockup as the page.
- Keep the large Gruk welcome banner on the shop page. Use a compact shared header on detail pages, forms and reports.
- Let product cards stack on smaller screens and simplify the banner so shopping controls remain easy to use.
- Reuse the same stylesheet, navigation and panel styles for Lab 9 and Lab 10 features.
- Keep design references in `images/mockups`, reusable website artwork in `static/images`, product artwork in `static/images/products`, and the shared stylesheet in `static/css`. Create folders as their files are added.
- The initial reusable artwork is `static/images/gruk.png`, `static/images/wood-background.png` and `static/images/parchment-background.png`. Gruk has a transparent background for placement over the shop layout. Check texture repetition at the intended display size when styling the pages.

## Shared Code Decisions

- Keep the starter's Python/Flask structure, SQL Server database and Docker setup.
- Carry forward the [Lab 7 Design Decisions](lab7-design-decisions.md) for database access, cart structure and order handling. Lab 8 replaces the earlier decision to preserve the starter's appearance with the theme described here.
- Use `get_connection()` from `db.py`, parameterized SQL with `?` placeholders, and connection cleanup in `finally`.
- Keep the current `session['productList']` cart structure and use `url_for()` for application links.
- Escape displayed values with `escape_html()`. Keep price formatting in the shared `format_currency()` helper.

## Currency and Product Data

- Elf ears replace the displayed currency label. Retain the existing numeric price fields and decimal arithmetic.
- Prefer whole-number prices for new themed products. Show `1 elf ear` and `25 elf ears`; preserve any fractional values in existing records accurately.
- Keep saved order prices in `orderproduct` unchanged when current product prices change. Order totals and history must use the saved prices.
- Preserve existing product IDs, order relationships and inventory quantities while introducing the theme. Do not delete referenced sample products just to shrink the catalogue.
- Add a repeatable themed-data setup step so resetting the database restores the theme. Check the existing reset flow before choosing how to integrate it.
- Keep one authoritative setup location for active product names, descriptions and prices. The shop-content document remains a place for creative ideas and asset notes.

## Product Details and Images

- Make product names in the listing link to a detail page using the product ID.
- Retrieve product information by ID with a parameterized query and show a clear message for a missing product.
- Display a URL image using `productImageURL` and an HTML `img` tag.
- Implement the image endpoint that reads binary `productImage` data and returns an image response with the appropriate content type. Demonstrate this through an `img` tag as well.
- The same artwork may be used to demonstrate both storage methods. Additional artwork is not required just because storage differs.
- Add an Add to Cart link with the actual product ID, name and price, plus a Continue Shopping link.
- Preserve the Lab 7 checkout behaviour that rechecks products and current prices before saving an order.

## Login Customer Information and Sales

- Validate the submitted user ID and password against the lab database using a parameterized query. Store the authenticated identity in the session and clear it on logout.
- Check login on the server before showing protected pages. Hiding a menu link is not an access check.
- Load customer information using the authenticated session identity, not a customer ID that the visitor can freely change in the URL. Handle a missing customer record clearly.
- Require login for the sales report, as specified in the Lab 8 marking guide. A separate administrator-role system is not part of the current plan.
- Calculate daily sales using `SUM(totalAmount)`, grouping by the date portion of the order timestamp and ordering by date.

## Shipment Transactions

- Ship an order from warehouse 1 using a single database transaction on one connection.
- Validate the requested order and obtain its ordered products and quantities.
- Create the shipment record and update all inventory within the transaction. Check sufficient inventory for every ordered quantity.
- Commit only after all operations succeed. On insufficient stock or any failed operation, roll back the shipment record and all inventory changes, including updates made before the failure.
- Show success only after commit. Show the reason for failure clearly; a Gruk quote may accompany the explanation.
- Verify order 1 as the supplied success case and order 3 as the supplied insufficient-stock case against freshly loaded data. Compare inventory and shipment records before and after each test.
- Reset test data when needed instead of repeatedly shipping the same order and expecting the original quantities.

## Scope and Implementation Order

- Lab 8 includes its required product details, both image methods, login, sales report, customer page and shipment transaction, plus the basic theme.
- Elf-ear balances, earning currency, combat, random loot, item statistics and animated or interactive Gruk behaviour are outside this plan.
- Save a small extra feature, such as best-selling gear based on sales, for Lab 9. Choose later additions from the Lab 10 marking sheet when needed.
- Inspect the existing implementation first, then implement and verify one required feature at a time. Apply the shared styling and catalogue without disrupting the shipment test data.

## Before Implementation

- Review the proposed catalogue and prices while mapping them to existing product IDs.
- Select or create the initial images and record their filenames and sources.

This document records the implementation plan. It does not indicate that the Lab 8 features have already been implemented or tested.
