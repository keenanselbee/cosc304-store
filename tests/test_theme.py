"""Small integration checks for the Gruk catalogue changes."""

from decimal import Decimal
from urllib.parse import parse_qs, urlparse

from theme import apply_theme
from support import DatabaseTest, Page, read_rows


class ThemeTests(DatabaseTest):
    def test_category_search_and_past_stock(self):
        product_id, name, price = self.create_product("search", Decimal("3.25"))
        for category, expected in (("", {product_id}), ("Weapons", {product_id}), ("Potions", set())):
            response = self.client.get("/listprod", query_string={"productName": name, "category": category})
            self.assertEqual(response.status_code, 200)
            actual = {int(parse_qs(urlparse(link).query)["id"][0]) for link in Page(response).links
                      if urlparse(link).path == "/addcart"}
            self.assertEqual(actual, expected)
            self.assertIn(name, response.get_data(as_text=True))
        for category in ("Unknown", "' OR 1=1 --"):
            self.assertEqual(self.client.get("/listprod", query_string={"category": category}).status_code, 400)
        past_id, past_name, past_price = read_rows(
            "SELECT TOP 1 p.productId,p.productName,p.productPrice FROM product p JOIN category c "
            "ON p.categoryId=c.categoryId WHERE c.categoryName='Past Stock'")[0]
        listing = self.client.get("/listprod", query_string={"productName": past_name})
        self.assertFalse(any(urlparse(link).path == "/addcart" for link in Page(listing).links))
        details = self.client.get("/product", query_string={"id": past_id})
        self.assertEqual(details.status_code, 200)
        self.assertIn("no longer offered", Page(details).text)
        self.assertFalse(any(urlparse(link).path == "/addcart" for link in Page(details).links))
        response = self.client.get("/addcart", query_string={"id": past_id, "name": past_name, "price": past_price})
        self.assertEqual(response.status_code, 400)
        with self.client.session_transaction() as session:
            self.assertFalse(session.get("productList"))

    def test_theme_reapplication_preserves_history_and_stock(self):
        # give a later order a price unrelated to the current product price
        product_id, name, price = self.create_product("history", Decimal("7.12"))
        self.create_order([(product_id, 2, Decimal("1.23"))])

        def snapshot():
            tables = ("product", "category", "ordersummary", "orderproduct", "productinventory", "shipment", "customer")
            return {table: sorted(read_rows("SELECT * FROM " + table), key=repr) for table in tables}

        before = snapshot()
        apply_theme()
        apply_theme()
        self.assertEqual(snapshot(), before)
        mismatches = read_rows("SELECT o.orderId FROM ordersummary o JOIN orderproduct p ON o.orderId=p.orderId "
                               "GROUP BY o.orderId,o.totalAmount HAVING o.totalAmount <> SUM(p.quantity*p.price)")
        self.assertEqual(mismatches, [])
