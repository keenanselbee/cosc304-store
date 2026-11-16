# Lab 8 Design Decisions

Build on the existing Python store with the required Lab 8 features and a simple cartoon fantasy theme. Keep the implementation small, readable and easy to maintain.

## Theme and Content

- The shop is **Gruk's Glorious Gear**, run by a cartoon orc merchant.
- Sell war axes, potions and equipment using **elf ears** as the displayed currency.
- Use [Lab 8 Shop Content](lab8-shop-content.md) for Gruk's personality, quotes, proposed products and image ideas. Item names and prices there remain a draft until implemented.
- Start with the proposed eight-item catalogue across Weapons, Armour and Potions. Map it onto existing product records without breaking order or inventory relationships.
- Keep the humour in descriptions and Gruk quotes, including the rotating shop speech bubble described below. Use clear navigation labels and functional messages.
- Keep internal names such as `product`, `price`, `customer` and `inventory` straightforward.

## Appearance

- **Mockup A (Timber Shop) is the selected visual direction:** [shop mockup](../images/mockups/lab8-shop-mockup.png). Keep this reference in `images/mockups`.
- Use a simple layout with dark brown backgrounds, readable parchment-coloured panels, and green and gold accents.
- The top wooden sign reads **ELF EARS ONLY** beside the bloody purple ear icon. Keep the shop name in the main welcome banner.
- Gruk's default speech bubble reads **Gruk is all ears, financially speaking.**
- Keep one shared stylesheet and reuse the existing page-generation approach with a small shared header/menu where practical. Avoid a new frontend framework or a broad rewrite.
- Use the static welcome Gruk and the selected pair of images for each themed product: one item-only image and one Gruk demonstration image.
- Use familiar labels such as Shop, Cart, Checkout, My Account, Sales Report, Login and Logout.
- Target the desktop browser used for the lab demonstration. A separate mobile layout is outside the current scope. Visual polish should not complicate the required behaviour.

## Frontend Implementation

- Use the selected mockup as a visual target, with small adjustments for readability and straightforward implementation.
- Reuse wood textures, the Gruk illustration and product pictures as image assets. Render headings, descriptions, prices, buttons and forms as real HTML rather than embedding the mockup as the page.
- Keep the immersive Gruk welcome scene on the shop page: shop interior behind Gruk, real HTML title and speech bubble, and a wooden counter edge directly above the shopping area. Do not put the whole scene inside a separate parchment card. Use a compact shared header on detail pages, forms and reports.
- Keep the desktop shop layout readable at the intended demonstration window size.
- Reuse the same stylesheet, navigation and panel styles for Lab 9 and Lab 10 features.
- Keep design references in `images/mockups`, reusable website artwork in `static/images`, product artwork in `static/images/products`, and the shared stylesheet in `static/css`. Create folders as their files are added.
- The initial reusable artwork is `static/images/gruk.png`, `static/images/wood-background.png` and `static/images/parchment-background.png`. Gruk has a transparent background for placement over the shop layout. Check texture repetition at the intended display size when styling the pages.

### Gruk's Shop Speech Bubble

- On each shop page load, show **Gruk is all ears, financially speaking.** first. Render it in the initial HTML so it also works without JavaScript.
- After the default, cycle through a shuffled pool of shop quotes from the Spare lines section in [Lab 8 Shop Content](lab8-shop-content.md). Show every quote once before reshuffling, and prevent the same quote appearing twice in a row across cycles. Include the default quote in subsequent shuffled cycles.
- Start with about 10 seconds per quote, including the initial default. Keep timing easy to adjust after seeing the page.
- Reveal each quote with a quick typewriter effect: letters appear progressively like game dialogue, rather than fading or sliding. Use about 20-30 ms per character as a starting point, including the first default quote when JavaScript is enabled. Start the reading interval after the full quote is visible.
- Give individual letters a subtle independent jitter as they type in, with a very gentle ongoing wiggle once revealed. Use small offsets and staggered timing so the text stays easy to read. The bubble itself and Gruk's illustration stay still; animate letters without moving their layout positions.
- Reserve enough bubble space for the longest quote so changes do not move the surrounding layout. Keep the text as real HTML.
- Provide a small Pause/Resume control for rotation and motion. When reduced motion is requested, show the default without automatic rotation or animation. Pause timers while the browser tab is hidden, without catching up on missed quotes.
- Use a small plain JavaScript script and CSS animations; no animation library, database table or API requests. Do not announce every decorative quote change through a screen-reader live region.
- This behaviour belongs to the shop welcome scene. Keep page-specific and transaction-related quotes fixed so random jokes never replace useful feedback.

## Shared Code Decisions

- Keep the starter's Python/Flask structure, SQL Server database and Docker setup.
- Carry forward the [Lab 7 Design Decisions](lab7-design-decisions.md) for database access, cart structure and order handling. Lab 8 replaces the earlier decision to preserve the starter's appearance with the theme described here.
- Use `get_connection()` from `db.py`, parameterized SQL with `?` placeholders, and connection cleanup in `finally`.
- Keep the current `session['productList']` cart structure and use `url_for()` for application links.
- Escape displayed values with `escape_html()`. Keep price formatting in the shared `format_currency()` helper.

## Currency and Product Data

- Elf ears replace the displayed currency label. Retain the existing numeric price fields and decimal arithmetic.
- Display prices as a number followed by `static/images/elf-ear-bloody.png` in a 32 px icon box, preserving the image's aspect ratio. Use the same icon at a larger size on the wooden sign. Keep `static/images/elf-ear.png` as the clean source variant.
- Prefer whole-number prices for new themed products; preserve any fractional values in existing records accurately. Retain `elf ear` or `elf ears` in accessible labels and plain-text fallbacks.
- Keep saved order prices in `orderproduct` unchanged when current product prices change. Order totals and history must use the saved prices. The explicit initial conversion of supplied grocery sample orders into themed demonstration data is the exception described below; normal theme reapplication must not reprice history.
- Preserve existing product IDs, order relationships and inventory quantities while introducing the theme. Do not delete referenced sample products just to shrink the catalogue.
- Add a repeatable themed-data setup step so resetting the database restores the theme. Check the existing reset flow before choosing how to integrate it.
- Keep one authoritative setup location for active product names, descriptions and prices. The shop-content document remains a place for creative ideas and asset notes.

## Product Details and Images

- Make product names in the listing link to a detail page using the product ID.
- Retrieve product information by ID with a parameterized query and show a clear message for a missing product.
- Display a URL image using `productImageURL` and an HTML `img` tag.
- Implement the image endpoint that reads binary `productImage` data and returns an image response with the appropriate content type. Demonstrate this through an `img` tag as well.
- For the selected theme, use the item-only image through `productImageURL` and the smaller Gruk demonstration through binary `productImage`. Both must appear on the detail page; no carousel or selectable gallery is needed. Two distinct images are a theme choice, not an additional lab requirement.
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
- Elf-ear balances, earning currency, combat, random loot, item statistics and character animation are outside this plan. The shop speech bubble's quote rotation and subtle motion are included as frontend polish.
- Save a small extra feature, such as best-selling gear based on sales, for Lab 9. Choose later additions from the Lab 10 marking sheet when needed.
- Inspect the existing implementation first, then implement and verify one required feature at a time. Apply the shared styling and catalogue without disrupting the shipment test data.

## Frontend Completion Plan

This is the implementation plan, not a claim that the frontend is complete. Keep changes on the current feature branch and review them against the saved backend baseline. Do not commit, merge or push automatically.

### Boundaries Around the Lab Code

- Preserve route URLs, form field names, HTTP methods, status codes, the cart session format and existing checkout behaviour. Checkout still asks for a customer ID; login is not a new prerequisite for placing an order.
- Preserve authentication checks, parameter binding, connection cleanup, order validation and price rechecking, saved-price calculations, and shipment transaction/rollback logic. Keep the teaching code and TODO separators recognizable; avoid unrelated refactoring.
- Change route HTML only where the shared layout cannot provide the needed presentation. Keep styling out of SQL and transaction blocks.
- Limit database-facing additions to catalogue setup, image/category fields for presentation, parameterized category filtering, and correct PNG/JPEG response types. Explain any additional required change before expanding scope.
- Do not add quantity editing, cart removal, registration, payment handling, stock reservation, administrator roles or other new shopping features during this pass.

### Shared Layout and Files

- Extend `html_utils.html_page()` as the single store-page wrapper. A small shared template is acceptable if it reduces duplicated markup; do not migrate every route to a new rendering architecture.
- Use one `static/css/shop.css` and one small `static/js/gruk.js`. Keep colours, spacing, typography and widths shared. Start with roughly 40 px outer wood margins on desktop.
- Keep the header consistent: ELF EARS ONLY sign, Shop, Cart, Orders, My Account, Admin and Login/Logout. Show the signed-in identity. Admin links to the existing sales report; it does not imply a new role system.
- Have `/` reuse the shop listing renderer so the landing page and `/listprod` use the same product query, controls and layout. Preserve `/listprod` and its `productName` parameter for existing links and tests.
- Keep all headings, buttons, prices and bubble text as HTML. Make the sign, counter edge and panels with CSS and existing textures. Use local/system fonts initially; no additional framework or asset generation is needed.
- Preserve full-resolution source PNGs. If needed, create smaller display copies under `static/images/web/`, record their source relationship in the asset log, and use the smaller files in pages and database image data. Preserve transparency and aspect ratio; use contained product images with reserved dimensions.
- Keep numeric money calculations unchanged. Format whole amounts without `.00` for themed display and retain two decimals for fractional amounts. Add the 32 px ear icon and an accessible currency label; never round away stored fractions.

### Catalogue and Reset Behaviour

- Use a single small `theme.py` setup module with an explicit command-line entry point and a callable setup function. Keep the eight active product definitions together there once implemented; the shop-content document then remains a creative reference.
- Map the eight selected items to existing product IDs 1-8 in catalogue order, after verifying those IDs exist. Validate names and image paths against database column lengths and check every required image before starting updates.
- Find or create Weapons, Armour and Potions categories for the eight current products and a Past Stock category for the remaining supplied products. Use parameterized updates in one transaction; repeating setup must not create duplicates.
- Theme all 29 supplied product records so existing order history contains no grocery names. Keep IDs 1-8 as the fully illustrated current catalogue. Give the other 21 products simple fantasy supply names, short descriptions and whole-number elf-ear prices; they are past stock and need no additional generated artwork. Remove their old grocery image references/data.
- Preserve product IDs, order-item product references, order/customer IDs, dates, ordered quantities, inventory quantities and shipments. Keep past-stock records available to order history and shipment processing; do not delete or merge them into the eight current products.
- Show only current-stock categories in the shop, search and category controls. All means all current shop products, initially eight. Use category membership rather than a hardcoded eight-ID limit, so future products in those categories can appear. Past-stock detail pages may explain that an item is no longer offered and omit the purchase link; ordinary shop navigation must not advertise past stock. Enforce the same past-stock restriction in the add-to-cart route with a small parameterized check if these detail pages remain accessible.
- Combine name and category filters, retaining the other value when either control changes, and provide a clear reset link. Query values remain bound parameters, including invalid-input handling. Update the existing search tests for this deliberate current-catalogue scope.
- Convert only the supplied sample orders to whole-number elf-ear unit prices as an explicit initial data conversion. Recalculate each affected `ordersummary.totalAmount` as the sum of its saved `orderproduct.quantity * orderproduct.price`. Daily sales then reflects those saved totals without changing the report query. This is curated demo data, not an exchange-rate conversion.
- Keep the sample-history conversion separate from ordinary catalogue reapplication: recognize the original sample rows by their expected contents, not just order IDs; skip already converted rows and stop on unexpected data rather than overwriting it. Back up affected data before applying the conversion to an existing database. Do not rewrite subsequently placed orders or prices when setup is rerun. Apply the conversion to fresh sample data after an intentional reset.
- Verify order 1 still succeeds and order 3 still fails for insufficient inventory on fresh themed sample data. Price and name changes must not change the quantities or stock conditions that make these demonstrations work.
- Apply the theme explicitly after the first Docker database initialization. After a deliberately requested reset through `/loaddata`, call the same setup function so reset restores the themed catalogue. Document the command and this behaviour in README; never run theme writes on ordinary page requests or reset existing data merely to apply the theme.
- A theme failure must roll back its updates and be reported accurately. A reset has already recreated the sample data before theme setup starts, so do not describe that entire operation as rolled back if theme setup fails.
- Return `image/png` for PNG database bytes and retain `image/jpeg` for existing JPEG data. Keep the image lookup query and missing-image responses intact.

### Page Coverage

| Page or state | Frontend work | Behaviour to preserve |
|---|---|---|
| Shop and search | Immersive welcome scene, quote animation, search, category filters and product cards | Blank/partial/no-match search, product links and add-to-cart links |
| Product details | Centred main item image, smaller Gruk image beneath, description, price and cart action | Both image delivery methods, actual product ID and missing-product responses |
| Cart | Simple rows, optional thumbnails, quantities, unit prices, subtotals and total | Existing calculations and session structure; quantities remain display-only |
| Checkout and order results | Clear customer-ID form, updated-price review, success and failure panels | Current price confirmation, commit/rollback and cart clearing only after success |
| Login and account | Shared form and customer-information styling | Existing validation, session identity, logout and protected-page redirects |
| Orders and sales | Readable tables and saved-price currency presentation | All-order listing and existing daily aggregate query |
| Shipment and setup | Plain styled results and clearly labelled lab utility links | Explicit shipment actions and database-reset confirmation; no automatic mutations |
| Empty/error states | Shared layout, concise messages and relevant return links | Existing error meaning and status codes |

- If cart thumbnails require a lookup, fetch image URLs for the cart IDs in one parameterized query. Do not add image bytes or new mandatory fields to the session cart, or replace session prices during rendering. Missing artwork must not prevent checkout.
- Keep shipment demo links and database setup reachable in a small lab-tools area, separate from ordinary shopping actions. Do not trigger either action while loading the shop.
- Build the shop layout first, then product details and cart, then reuse the same panels for the remaining pages. Avoid separate bespoke designs for forms and reports.

### Animation and Readability

- Implement the speech behaviour above only after the static shop is usable. Keep word wrapping normal even when individual letters use spans; reserve the full quote's layout while it types so words do not jump around.
- Keep one complete accessible sentence separate from the decorative animated letters. Do not have screen readers read individual letter spans or announce every automatic change. Pause during typing should reveal the complete current quote and stop rotation/jitter; Resume starts a fresh reading interval.
- With JavaScript disabled, the default quote, navigation, search, filters and checkout remain functional. Reduced-motion mode has complete static text and no letter jitter or automatic rotation.
- Use the desktop composition from the mockups. Keep Gruk from covering text or controls; mobile navigation, stacked mobile layouts and phone-specific grid changes are outside this pass.
- Use visible keyboard focus, labelled fields, descriptive product-image alternatives and decorative-image empty alternatives. Keep readable contrast and touch-sized controls. Wrap wide reports in local horizontal scrolling rather than making the entire page overflow.

### Implementation Order and Completion Checks

1. Inspect the baseline diff and run the existing Lab 7/8 suite against the current local database when Docker is available. Record pre-existing failures separately; do not assume earlier test results describe the current checkout.
2. Build the shared shell, currency display and static shop scene. Inspect the desktop layout at the intended demonstration window size before copying the styling to other pages.
3. Add repeatable catalogue setup and the small query/image-type changes, then connect product cards, category search, both detail images and cart presentation. Apply setup without resetting the database.
4. Finish forms, reports, order results and error states. Add the quote animation last so it cannot block shopping behaviour.
5. Run the complete Lab 7/8 suite after integration. Add focused coverage for combined category/name filtering and repeatable theme setup. Update presentation-sensitive assertions to inspect product content rather than all page images, and to accept the intended currency markup; retain checks of actual prices, image bytes, authentication and rollback behaviour.
6. Verify setup twice in a disposable test database or with recorded before/after data: no duplicate categories, identical mapped content, and no further changes to converted order prices/totals on the second run. Check that each converted sample total equals its saved lines, later orders stay untouched, and order references, quantities, dates, inventory and shipments remain unchanged. Check that reset plus theme works separately; never exercise destructive reset against unprotected project data.
7. Walk through search -> details -> repeated cart additions -> checkout -> saved order, plus changed prices, empty/no-match/missing-product states, login/logout, customer information and sales. Use disposable records for shipment checks; retain the supplied order 1/order 3 demonstration instructions for freshly loaded lab data.
8. Inspect the actual pages at the intended desktop demonstration window size, using keyboard navigation, reduced motion and JavaScript disabled. Check image requests, image content types, layout overflow, quote timing and pause/resume. All important actions must be usable and errors understandable. Mobile layout testing is outside this pass.
9. Update README's stale TODO/login-failure text, setup instructions and the grouped frontend provenance entry with the files actually changed and checks actually completed. Review the final diff specifically for unintended edits to protected backend logic.

### Frontend Provenance

- Add a **Gruk frontend and theme** section to `docs/PROVENANCE.md` when implementation starts, with one grouped entry for shared presentation code, route presentation edits and catalogue/image integration. List the actual main paths concisely rather than adding a row per file.
- Distinguish newly generated frontend code from AI revisions to existing route presentation. Explicitly describe the limited query/setup/image-type changes; do not imply all required Lab 8 backend code in those files was generated as part of the frontend.
- Keep existing required-backend entries separate. Keep the single website artwork and single mockup entries; individual image prompts and source relationships belong in the asset log.
- Record validation only after it runs. The plan and documentation edits remain covered by their existing documentation provenance entries.

This document records the implementation plan. It does not indicate that the Lab 8 features have already been implemented or tested.
