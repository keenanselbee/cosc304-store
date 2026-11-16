"""Lab 7 checks using unittest and the local SQL Server database."""

import unittest
from decimal import Decimal
from urllib.parse import parse_qs, urlparse

from app import app
from routes import order
from support import DatabaseTest, Page, read_rows


class Lab7Tests(DatabaseTest):
    def setUp(self):
        super().setUp()
        self.products = [self.create_product("A", Decimal("12.34")),
                         self.create_product("B", Decimal("7.89"))]

    def add_product(self, product, **changes):
        product_id, name, price = product
        values = {"id": product_id, "name": name, "price": str(price)}
        values.update(changes)
        response = self.client.get("/addcart", query_string=values, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def submit(self, **changes):
        return self.client.post("/order", data={"customerId": str(self.customer_id), **changes})

    def cart(self):
        with self.client.session_transaction() as session:
            return session.get("productList", {})

    def assert_no_saved_orders(self):
        for order_id in self.order_ids:
            self.assertEqual(read_rows("SELECT orderId FROM ordersummary WHERE orderId = ?", [order_id]), [])
            self.assertEqual(read_rows("SELECT orderId FROM orderproduct WHERE orderId = ?", [order_id]), [])

    def test_search_blank_partial_and_no_matches(self):
        for term in ("", self.token, self.products[0][1]):
            with self.subTest(search=term):
                response = self.client.get("/listprod", query_string={"productName": term})
                self.assertEqual(response.status_code, 200)
                page = Page(response)
                actual = {int(parse_qs(urlparse(link).query)["id"][0]) for link in page.links
                          if urlparse(link).path == "/addcart"}
                expected = {row[0] for row in read_rows(
                    "SELECT productId FROM product WHERE productName LIKE ?", [f"%{term}%"])}
                self.assertEqual(actual, expected)
        for term in (self.token + "missing", "' OR 1=1 --"):
            response = self.client.get("/listprod", query_string={"productName": term})
            self.assertEqual(response.status_code, 200)
            self.assertFalse(any(urlparse(link).path == "/addcart" for link in Page(response).links))

    def test_repeated_additions_and_cart_totals(self):
        self.add_product(self.products[0])
        self.add_product(self.products[0])
        self.add_product(self.products[1])
        cart = self.cart()
        self.assertEqual(cart[str(self.products[0][0])]["quantity"], 2)
        self.assertEqual(cart[str(self.products[1][0])]["quantity"], 1)
        response = self.client.get("/showcart")
        self.assertEqual(response.status_code, 200)
        page = Page(response)
        for product_id, name, price in self.products:
            self.assertIn(name, page.text)
        self.assertIn("24.68", page.text)
        self.assertIn("32.57", page.text)
        self.assertIn("/checkout", page.links)

    def test_search_cart_checkout_and_saved_order(self):
        self.watch(order, "ordersummary")
        product_id, name, price = self.products[0]
        response = self.client.get("/listprod", query_string={"productName": name})
        link = next(link for link in Page(response).links if urlparse(link).path == "/addcart")
        self.assertEqual(self.client.get(link, follow_redirects=True).status_code, 200)
        self.add_product(self.products[0])
        self.add_product(self.products[1])
        self.assertEqual(self.client.get("/checkout").status_code, 200)
        self.assertEqual(self.submit().status_code, 200)
        self.assertFalse(self.cart())
        self.assertTrue(self.connections[-1].committed)
        self.assertEqual(len(self.order_ids), 1)
        order_id = self.order_ids[0]
        self.assertEqual(read_rows("SELECT customerId, totalAmount FROM ordersummary WHERE orderId = ?",
                                   [order_id]), [(self.customer_id, Decimal("32.57"))])
        self.assertEqual(read_rows("SELECT productId, quantity, price FROM orderproduct "
                                   "WHERE orderId = ? ORDER BY productId", [order_id]),
                         [(product_id, 2, price), (self.products[1][0], 1, self.products[1][2])])
        self.assertIn(str(order_id), Page(self.client.get("/listorder")).words)
        self.assertEqual(self.submit().status_code, 400)
        self.assertEqual(len(self.order_ids), 1)

    def test_order_history_uses_saved_prices(self):
        product_id, name, current_price = self.products[0]
        saved_price = Decimal("4.56")
        order_id = self.create_order([(product_id, 3, saved_price)])
        response = self.client.get("/listorder")
        self.assertEqual(response.status_code, 200)
        page = Page(response)
        customer_name = " ".join(read_rows("SELECT firstName, lastName FROM customer WHERE customerId = ?",
                                            [self.customer_id])[0])
        for value in (str(order_id), str(self.customer_id), customer_name, name, "3", "4.56", "13.68"):
            self.assertIn(value, page.text)
        self.assertNotEqual(saved_price, current_price)
        # check the saved unit price beside our unique product name
        start = page.text.index(name) + len(name)
        self.assertRegex(page.text[start:], r"^\s+3\s+\$?4\.56\s+\$?13\.68")

    def test_changed_price_requires_confirmation(self):
        self.watch(order, "ordersummary")
        self.add_product(self.products[0], price="0", name="<script>fake</script>")
        response = self.submit(confirm="1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.order_ids, [])
        self.assertNotIn("<script>fake</script>", response.get_data(as_text=True))
        self.assertEqual(Decimal(next(iter(self.cart().values()))["price"]), self.products[0][2])
        self.assertEqual(self.submit().status_code, 200)
        self.assertEqual(len(self.order_ids), 1)

    def test_invalid_customer_preserves_cart(self):
        self.watch(order, "ordersummary")
        self.add_product(self.products[0])
        original = self.cart()
        for value in ("", "0", "-1", "1.5", "2147483648", "1 OR 1=1", "2147483647"):
            with self.subTest(customer=value):
                self.assertEqual(self.submit(customerId=value).status_code, 400)
                self.assertEqual(self.cart(), original)
                self.assertEqual(self.order_ids, [])

    def test_empty_cart_and_missing_product(self):
        self.watch(order, "ordersummary")
        self.assertEqual(self.submit().status_code, 400)
        self.add_product((2147483647, "Missing product", Decimal("1.00")))
        original = self.cart()
        self.assertEqual(self.submit().status_code, 400)
        self.assertEqual(self.cart(), original)
        self.assertEqual(self.order_ids, [])

    def test_invalid_cart_values_and_total_overflow(self):
        self.watch(order, "ordersummary")
        for field, value in (("quantity", 0), ("quantity", -1), ("quantity", 1.5), ("quantity", True),
                             ("price", "NaN"), ("price", "bad"), ("quantity", 2147483647)):
            with self.subTest(field=field, value=value):
                self.client = app.test_client()
                self.add_product(self.products[0])
                with self.client.session_transaction() as session:
                    cart = session["productList"]
                    next(iter(cart.values()))[field] = value
                    session["productList"] = cart
                original = self.cart()
                self.assertEqual(self.submit().status_code, 400)
                self.assertEqual(self.cart(), original)
                self.assertEqual(self.order_ids, [])

    def test_second_item_failure_rolls_back(self):
        self.watch(order, "ordersummary", fail_sql="INSERT INTO orderproduct", fail_at=2)
        self.assert_failed_order_rolls_back()

    def test_commit_failure_rolls_back(self):
        self.watch(order, "ordersummary", fail_commit=True)
        self.assert_failed_order_rolls_back()

    def assert_failed_order_rolls_back(self):
        for product in self.products:
            self.add_product(product)
        original = self.cart()
        with self.assertLogs(app.logger, level="ERROR"):
            self.assertEqual(self.submit().status_code, 500)
        self.assertEqual(len(self.order_ids), 1)
        self.assertTrue(self.connections[-1].rolled_back)
        self.assertFalse(self.connections[-1].committed)
        self.assertEqual(self.cart(), original)
        self.assert_no_saved_orders()


if __name__ == "__main__":
    unittest.main()
