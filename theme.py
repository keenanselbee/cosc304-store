"""Repeatable Gruk catalogue setup, separate from the required lab routes."""

from datetime import datetime
from decimal import Decimal
from pathlib import Path
import re

from db import get_connection

ROOT = Path(__file__).resolve().parent
# id, name, elf ears, category, description, image stem
CATALOGUE = [
    (1, "Gruk's Slightly Used War Axe", 40, 'Weapons',
     'A sturdy iron axe with a wrapped handle and a few stories in the blade. Previous owner no longer needs it.',
     'slightly-used-war-axe'),
    (2, 'The Bigger Argument', 75, 'Weapons',
     'A heavy double-headed war axe for when the smaller axe fails to make your point. Requires both hands and considerable confidence.',
     'the-bigger-argument'),
    (3, 'Politely Dented Shield', 30, 'Armour',
     'A round wooden shield with an iron rim. Every dent is proof it was standing between someone and a problem.',
     'politely-dented-shield'),
    (4, 'Helmet of Almost Wisdom', 25, 'Armour',
     'A solid iron helmet that protects your head while you continue making the same decisions.',
     'helmet-of-almost-wisdom'),
    (5, 'Boots of Strategic Retreat', 20, 'Armour',
     'Thick leather boots for long journeys and sudden changes of plan. Gruk calls it tactical walking.',
     'boots-of-strategic-retreat'),
    (6, 'Suspicious Red Potion', 10, 'Potions',
     'A corked bottle of bright red liquid with a very confident health symbol. Probably health. Definitely red.',
     'suspicious-red-potion'),
    (7, 'Blue Thinking Juice', 15, 'Potions',
     'A blue potion favoured by spellcasters. Gruk tried some once. Had two thoughts. Did not enjoy it.',
     'blue-thinking-juice'),
    (8, 'Bottled Bad Idea', 12, 'Potions',
     'A fizzy green potion with a crooked warning label. For adventurers who believe reading instructions ruins the surprise.',
     'bottled-bad-idea'),
    (9, 'Goblin Pocket Hammer', 18, 'Past Stock',
     "From Gruk's older stock. No longer offered in the shop.",
     None),
    (10, 'Rusty Throwing Knife', 15, 'Past Stock',
     "From Gruk's older stock. No longer offered in the shop.",
     None),
    (11, "Apprentice's Bent Wand", 22, 'Past Stock',
     "From Gruk's older stock. No longer offered in the shop.",
     None),
    (12, 'Moth-Eaten Mage Robe', 24, 'Past Stock',
     "From Gruk's older stock. No longer offered in the shop.",
     None),
    (13, 'Secondhand Chainmail', 28, 'Past Stock',
     "From Gruk's older stock. No longer offered in the shop.",
     None),
    (14, 'Goblin Lockpick Set', 9, 'Past Stock',
     "From Gruk's older stock. No longer offered in the shop.",
     None),
    (15, 'Dragonproof Mittens', 16, 'Past Stock',
     "From Gruk's older stock. No longer offered in the shop.",
     None),
    (16, 'Wobbly Spear', 25, 'Past Stock',
     "From Gruk's older stock. No longer offered in the shop.",
     None),
    (17, 'Spare Troll Tooth', 7, 'Past Stock',
     "From Gruk's older stock. No longer offered in the shop.",
     None),
    (18, 'Cracked Crystal Ball', 30, 'Past Stock',
     "From Gruk's older stock. No longer offered in the shop.",
     None),
    (19, "Gruk's Sharpening Stone", 6, 'Past Stock',
     "From Gruk's older stock. No longer offered in the shop.",
     None),
    (20, 'Suspiciously Strong Rope', 12, 'Past Stock',
     "From Gruk's older stock. No longer offered in the shop.",
     None),
    (21, 'Dungeon Bedroll', 14, 'Past Stock',
     "From Gruk's older stock. No longer offered in the shop.",
     None),
    (22, 'Potion of Loud Snoring', 8, 'Past Stock',
     "From Gruk's older stock. No longer offered in the shop.",
     None),
    (23, 'Ogre-Sized Mug', 10, 'Past Stock',
     "From Gruk's older stock. No longer offered in the shop.",
     None),
    (24, 'Slightly Cursed Compass', 19, 'Past Stock',
     "From Gruk's older stock. No longer offered in the shop.",
     None),
    (25, 'Goblin Lantern', 17, 'Past Stock',
     "From Gruk's older stock. No longer offered in the shop.",
     None),
    (26, 'Emergency Smoke Flask', 11, 'Past Stock',
     "From Gruk's older stock. No longer offered in the shop.",
     None),
    (27, 'Rusty Bear Trap', 21, 'Past Stock',
     "From Gruk's older stock. No longer offered in the shop.",
     None),
    (28, 'Lucky Bone Charm', 4, 'Past Stock',
     "From Gruk's older stock. No longer offered in the shop.",
     None),
    (29, 'Almost Eternal Torch', 8, 'Past Stock',
     "From Gruk's older stock. No longer offered in the shop.",
     None)]
SAMPLE_ORDERS = [
    (1, 1, "2026-10-15 10:25:55", "91.70", [(1, 1, "18"), (5, 2, "21.35"), (10, 1, "31")]),
    (2, 2, "2026-10-16 18:00:00", "106.75", [(5, 5, "21.35")]),
    (3, 3, "2026-10-15 03:30:22", "140", [(6, 2, "25"), (7, 3, "30")]),
    (4, 2, "2026-10-17 05:45:11", "327.85", [(3, 4, "10"), (8, 3, "40"), (13, 3, "23.25"),
                                           (28, 2, "21.05"), (29, 4, "14")]),
    (5, 5, "2026-10-15 10:25:55", "277.40", [(5, 4, "21.35"), (19, 2, "81"), (20, 3, "10")])]


def apply_theme(database="orders"):
    # check files before changing any data
    pictures = {}
    for product_id, name, price, category, description, stem in CATALOGUE:
        if len(name) > 40 or len(description) > 1000:
            raise ValueError("Theme text is too long")
        if stem:
            image_url = f"images/products/{stem}.png"
            item_file = ROOT / "static" / image_url
            gruk_file = ROOT / "static/images/products" / f"{stem}-gruk.png"
            if not item_file.is_file() or not gruk_file.is_file() or len(image_url) > 100:
                raise ValueError(f"Missing image for {name}")
            pictures[product_id] = (image_url, gruk_file.read_bytes())
        else:
            pictures[product_id] = (None, None)

    # the original names distinguish fresh sample data from an already themed database
    ddl = (ROOT / "ddl/SQLServer_orderdb.ddl").read_text(encoding="utf-8-sig")
    original_names = [name.replace("''", "'") for name in re.findall(
        r"INSERT product\(.*?VALUES \('((?:''|[^'])*)'", ddl)]
    connection = get_connection(database)
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT productId, productName FROM product WHERE productId BETWEEN 1 AND 29 ORDER BY productId")
        actual = [tuple(row) for row in cursor.fetchall()]
        original = list(enumerate(original_names, 1))
        themed = [(item[0], item[1]) for item in CATALOGUE]
        if actual not in (original, themed):
            raise ValueError("Sample products do not match the original or themed catalogue")
        convert_history = actual == original

        # only convert the known seed orders on the first application
        if convert_history:
            for order_id, customer_id, date, total, items in SAMPLE_ORDERS:
                cursor.execute("SELECT customerId, orderDate, totalAmount FROM ordersummary WHERE orderId = ?", [order_id])
                row = cursor.fetchone()
                expected = (customer_id, datetime.fromisoformat(date), Decimal(total))
                cursor.execute("SELECT productId, quantity, price FROM orderproduct WHERE orderId = ? ORDER BY productId", [order_id])
                lines = [tuple(line) for line in cursor.fetchall()]
                expected_lines = [(pid, qty, Decimal(price)) for pid, qty, price in items]
                if row is None or tuple(row) != expected or lines != expected_lines:
                    raise ValueError(f"Sample order {order_id} has changed; theme conversion stopped")

        category_ids = {}
        for name in ("Weapons", "Armour", "Potions", "Past Stock"):
            cursor.execute("SELECT categoryId FROM category WHERE categoryName = ?", [name])
            row = cursor.fetchone()
            if row is None:
                cursor.execute("INSERT INTO category (categoryName) OUTPUT INSERTED.categoryId VALUES (?)", [name])
                row = cursor.fetchone()
            category_ids[name] = row[0]
        for product_id, name, price, category, description, stem in CATALOGUE:
            image_url, image_data = pictures[product_id]
            cursor.execute("""UPDATE product SET productName = ?, productPrice = ?, categoryId = ?,
                              productDesc = ?, productImageURL = ?, productImage = ? WHERE productId = ?""",
                           [name, price, category_ids[category], description, image_url, image_data, product_id])

        if convert_history:
            prices = {item[0]: item[2] for item in CATALOGUE}
            for order_id, customer_id, date, total, items in SAMPLE_ORDERS:
                for product_id, quantity, old_price in items:
                    cursor.execute("UPDATE orderproduct SET price = ? WHERE orderId = ? AND productId = ?",
                                   [prices[product_id], order_id, product_id])
                cursor.execute("""UPDATE ordersummary SET totalAmount =
                                  (SELECT SUM(quantity * price) FROM orderproduct WHERE orderId = ?)
                                  WHERE orderId = ?""", [order_id, order_id])
        # retire the earlier empty demo account without losing related records
        cursor.execute("SELECT customerId FROM customer WHERE userid = ? AND customerId <> 1", ["gruk"])
        old_accounts = cursor.fetchall()
        for old_account in old_accounts:
            old_id = old_account[0]
            cursor.execute("""SELECT customerId FROM ordersummary WHERE customerId = ?
                              UNION ALL SELECT customerId FROM paymentmethod WHERE customerId = ?
                              UNION ALL SELECT customerId FROM review WHERE customerId = ?""",
                           [old_id, old_id, old_id])
            if cursor.fetchone() is not None:
                raise ValueError("The old Gruk account has related records; account change stopped")
            cursor.execute("DELETE FROM customer WHERE customerId = ?", [old_id])

        # theme customer 1 so the sample orders still belong to the same customer
        cursor.execute("""UPDATE customer SET firstName = ?, lastName = ?, email = ?, phonenum = ?,
                          address = ?, city = ?, state = ?, postalCode = ?, country = ?,
                          userid = ?, password = ? WHERE customerId = 1""",
                       ["Gruk", "Bargaintusk", "gruk@example.com", "555-0108", "8 Anvil Lane",
                        "Stonefang", "Ironlands", "GG8 001", "Orc Territories", "gruk", "axe"])
        if cursor.rowcount != 1:
            raise ValueError("Sample customer 1 is missing; account change stopped")
        connection.commit()
        return "Gruk catalogue ready; sample orders converted" if convert_history else "Gruk catalogue ready; saved orders unchanged"
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    print(apply_theme())
