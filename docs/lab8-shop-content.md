# Lab 8 Shop Content

Gruk's Glorious Gear is a cartoon fantasy shop selling war axes, potions and equipment for elf ears. This document collects the proposed shop copy and image ideas before they are added to the application.

The shop name and elf-ear currency are agreed decisions. The character details, quotes, items and prices below are a first draft that we can adjust.

## Shop Identity

| Element | Copy |
|---|---|
| Shop name | Gruk's Glorious Gear |
| Tagline | Sharp axes. Strong potions. No refunds. |
| Welcome heading | Gear up with Gruk |
| Welcome text | War axes, sturdy armour and potions of mostly known origin. Browse Gruk's finest supplies before your next questionable adventure. |
| Wooden sign | ELF EARS ONLY, followed by the bloody purple ear icon |
| Default speech bubble | Gruk is all ears, financially speaking. |
| Main button | Browse Gear |
| Footer line | Gruk's Glorious Gear. Proudly counting ears since breakfast. |

## Meet Gruk

Gruk is a broad green orc with two large tusks, one nicked eyebrow and a worn leather merchant's apron. He stands behind a wooden counter with an axe on display and a few colourful potion bottles nearby. His expression is a confident grin: he is delighted that someone has finally come to appreciate his stock.

He is proud, practical and a little too enthusiastic about axes. He understands selling better than spelling and is suspicious of anything described as delicate. He insists that dents are evidence of quality testing. He remembers repeat customers because repeat customers are good for business.

Use an original cartoon orc design with the chunky shapes and exaggerated equipment of fantasy games. One static illustration is enough for the first version.

### Gruk's voice

- Short sentences and occasional missing words, while remaining easy to read.
- Refers to himself as Gruk rather than using I.
- Confident about equipment, less certain about potion ingredients.
- Jokes about his stock and salesmanship more often than the customer.
- Show one short quote at a time. The shop welcome bubble rotates through quotes; other page and event quotes stay fixed.
- Navigation, form labels and error explanations use ordinary clear English.
- Product descriptions are flavour text, not promises of game mechanics.

## Starter Catalogue

Eight proposed products across three categories. Prices are per item in elf ears. Product IDs will be mapped to the existing database during implementation.

| Product | Category | Price | Description |
|---|---|---:|---|
| Gruk's Slightly Used War Axe | Weapons | 40 | A sturdy iron axe with a wrapped handle and a few stories in the blade. Previous owner no longer needs it. |
| The Bigger Argument | Weapons | 75 | A heavy double-headed war axe for when the smaller axe fails to make your point. Requires both hands and considerable confidence. |
| Politely Dented Shield | Armour | 30 | A round wooden shield with an iron rim. Every dent is proof it was standing between someone and a problem. |
| Helmet of Almost Wisdom | Armour | 25 | A solid iron helmet that protects your head while you continue making the same decisions. |
| Boots of Strategic Retreat | Armour | 20 | Thick leather boots for long journeys and sudden changes of plan. Gruk calls it tactical walking. |
| Suspicious Red Potion | Potions | 10 | A corked bottle of bright red liquid labelled HEALTH in very confident handwriting. Probably health. Definitely red. |
| Blue Thinking Juice | Potions | 15 | A blue potion favoured by spellcasters. Gruk tried some once. Had two thoughts. Did not enjoy it. |
| Bottled Bad Idea | Potions | 12 | A fizzy green potion with a crooked warning label. For adventurers who believe reading instructions ruins the surprise. |

### Past Stock and Sample Orders

The storefront starts with the eight products above. The other 21 supplied product records will become past fantasy stock so existing order history also fits Gruk's shop. They need simple themed names and descriptions, not another set of generated images or product cards. Keep their original IDs and order relationships.

The supplied demonstration orders will receive whole-number elf-ear unit prices and matching recalculated totals during the initial theme conversion. Keep dates, customers, ordered quantities and inventory quantities unchanged so the Lab 8 shipment examples still work. Later purchases retain their saved prices. The setup module will hold the final mapping and values; see [Catalogue and Reset Behaviour](lab8-design-decisions.md#catalogue-and-reset-behaviour).

### Category introductions

| Category | Short introduction |
|---|---|
| Weapons | For problems that stand too close. |
| Armour | Put something sturdy between you and your decisions. |
| Potions | Colourful solutions. Read label. If label exists. |

## Page and Event Quotes

These are fixed lines for the relevant page or event. The shop welcome line appears first before the speech bubble begins its shuffled quote cycle, as described in [Lab 8 Design Decisions](lab8-design-decisions.md#gruks-shop-speech-bubble). Other page and event lines stay fixed.

| Location or event | Gruk's line |
|---|---|
| Shop welcome | Gruk is all ears, financially speaking. |
| Product details | Gruk would use this himself. But Gruk would rather sell it. |
| Empty cart | Nothing? You fighting dragon with manners? |
| Cart with items | Good pile. Could be bigger pile. |
| Checkout | Count gear. Count ears. Then we do business. |
| Successful order | Good choice. Gruk almost kept that one. |
| Login page | Gruk knows faces. Website wants password. |
| Customer page | Ah, returning customer. Gruk likes those. |
| Logout | Come back with more ears. Or just more ears. |
| No search results | Gruk checked shelves. Even the suspicious shelf. |
| Product not found | Gruk cannot find that one. Might have sold it. Might be sitting on it. |
| Sales report | Gruk calls this counting. Accountant calls it reporting. |
| Successful shipment | All packed. Gruk used the good crate. |
| Insufficient inventory | Not enough gear. Gruk refuses to ship half an adventure. |

### Spare lines

Use these as the initial shop speech-bubble pool after the default welcome quote. Keep them in one frontend quote list when implemented.

- "You bring ears. Gruk brings gear. Good arrangement."
- "Browse all you want. Touch cursed shelf at own risk."
- "That dent? Premium dent."
- "Sharp end goes away from customer. Usually."
- "Gruk tested the shield. Wall lost."
- "No haggling. Gruk already argued with price tag."

## Clear Messages Alongside the Jokes

The functional message appears first. A Gruk quote may follow as a separate sentence or short line.

| Situation | Functional message |
|---|---|
| Login required | Please log in to view this page. |
| Invalid credentials | User ID or password is incorrect. |
| Missing customer record | Customer information could not be found for this account. |
| Empty cart at checkout | Your cart is empty. Add an item before checking out. |
| No matching products | No products matched your search. Try another name or category. |
| Missing product | This product could not be found. Return to the shop to browse available gear. |
| Successful order | Order placed successfully. Your order number is {order_id}. |
| Failed order | Your order could not be placed. Your cart has been kept. |
| Successful shipment | Shipment completed for order {order_id}. Inventory has been updated. |
| Insufficient stock after rollback | Shipment cancelled: not enough {product_name} in warehouse 1. No shipment was created and inventory was not changed. |

Placeholders represent values supplied by the application. Only display success or rollback claims after the corresponding database operation has actually succeeded.

## Currency and Labels

- Display each price as a number followed by the bloody purple ear icon in a 32 px box. Use `elf ear` or `elf ears` in accessible labels and plain-text fallbacks rather than a dollar sign.
- Use whole-number prices for the themed catalogue. Preserve accurate decimal values if existing data contains fractions; do not silently round stored order amounts for the theme.
- Use `Price`, `Quantity` and `Total` as the standard shopping labels.
- Keep `Shop`, `Cart`, `Checkout`, `My Account`, `Sales Report`, `Login` and `Logout` easy to identify.
- Use `Add to Cart` and `Continue Shopping` on product pages.
- Elf ears are the displayed currency. This content does not require a wallet, earning system, combat or item statistics.

## Image Notes

Use the same simple cartoon style for all products: chunky outlines, readable silhouettes, warm highlights and a plain or transparent background. Keep the illustrations clear at small sizes.

| Asset | Image direction |
|---|---|
| Gruk | Green orc merchant with large tusks, leather apron and an eager grin behind a wooden counter |
| Slightly Used War Axe | Single iron axe head with a small nick and a brown wrapped handle |
| The Bigger Argument | Oversized double-headed axe with a thick wooden handle |
| Politely Dented Shield | Round wooden shield with iron rim and one obvious dent in the centre boss |
| Helmet of Almost Wisdom | Squat iron helmet with a crooked crest |
| Boots of Strategic Retreat | Heavy brown boots with oversized buckles |
| Suspicious Red Potion | Round red bottle with a cork and a simple health symbol |
| Blue Thinking Juice | Tall blue bottle with a small star symbol |
| Bottled Bad Idea | Uneven green bottle with bubbles and a warning symbol |
| Currency icon | Purple pointed cartoon ear with crimson blood, readable at 32 px; use a larger version on the wooden sign |

The selected artwork provides two images per product: a standalone item for URL-based display and a smaller Gruk demonstration for database-backed display. The welcome scene uses its own static Gruk illustration. The two storage methods do not require different artwork, but the selected pair makes the product page more useful and playful.

## Maintaining the Content

### Generated assets

| Asset | File | Intended use |
|---|---|---|
| Gruk | `static/images/gruk.png` | Transparent character illustration for the welcome banner |
| Wood texture | `static/images/wood-background.png` | Warm dark timber background for the page and navigation |
| Parchment texture | `static/images/parchment-background.png` | Light background for content panels and product cards |
| Clean elf ear | `static/images/elf-ear.png` | Transparent source variant without blood |
| Bloody elf ear | `static/images/elf-ear-bloody.png` | Currency icon beside prices and on the wooden sign |
| Shop interior | `static/images/shop-interior.png` | Cluttered weapons-and-potions background behind the welcome Gruk |
| Eight product pairs | `static/images/products/` | Full-resolution selected item sources and matching `-gruk` demonstration images |

These assets were generated with OpenAI's built-in image generation tool using the selected visual references. Retained prompts and summaries of earlier edits are recorded in [Lab 8 Asset Prompts](lab8-asset-prompts.json), with a general credit in [Provenance](PROVENANCE.md). The eight product pairs and shop interior have been selected and imported. Texture repetition, final sizing and composition will be checked when the assets are used in the page layout. Earlier image directions above are creative drafts; the selected source images take precedence for visual details.

This file holds the creative draft, reusable quotes and image notes. When the catalogue is implemented, the database setup script becomes the source of truth for active product names, descriptions and prices. Record its path here at that point and keep unused ideas in this document.

Draft prepared with ChatGPT during the Lab 8 planning conversation. Include the conversation link in the project's source documentation when available.
