"""Run against the lab database with python -m unittest discover -s tests -v."""

import re
import unittest
from decimal import Decimal
from html import unescape
from unittest.mock import patch

from app import app
from db import get_connection
from routes import order


class TrackedConnection:
    def __init__(self, connection, order_ids, fail_on_item=None, fail_commit=False):
        self.connection = connection
        self.order_ids = order_ids
        self.fail_on_item = fail_on_item
        self.fail_commit = fail_commit
        self.item_count = 0
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def cursor(self):
        self.sql_cursor = self.connection.cursor()
        return self

    def execute(self, sql, *parameters):
        self.inserting_order = sql.startswith("INSERT INTO ordersummary")
        if sql.startswith("INSERT INTO orderproduct"):
            self.item_count += 1
            if self.item_count == self.fail_on_item:
                raise RuntimeError("Simulated line item failure")
        self.sql_cursor.execute(sql, *parameters)
        return self

    def fetchone(self):
        row = self.sql_cursor.fetchone()
        if self.inserting_order and row is not None:
            self.order_ids.append(row[0])
        return row

    def commit(self):
        if self.fail_commit:
            raise RuntimeError("Simulated commit failure")
        self.connection.commit()
        self.committed = True

    def rollback(self):
        self.connection.rollback()
        self.rolled_back = True

    def close(self):
        self.connection.close()
        self.closed = True


class OrderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        connection = get_connection()
        try:
            cursor = connection.cursor()
            cls.customer_id = cursor.execute(
                "SELECT TOP 1 customerId FROM customer ORDER BY customerId").fetchone()[0]
            cls.products = cursor.execute(
                "SELECT TOP 2 productId, productName, productPrice FROM product "
                "WHERE productPrice > 0 ORDER BY productId").fetchall()
            if len(cls.products) != 2:
                raise RuntimeError("Tests require two products with positive prices")
        finally:
            connection.close()

    def setUp(self):
        self.client = app.test_client()
        self.order_ids = []
        self.connections = []
        self.fail_on_item = None
        self.fail_commit = False

        def tracked_connection():
            connection = TrackedConnection(get_connection(), self.order_ids,
                                           self.fail_on_item, self.fail_commit)
            self.connections.append(connection)
            return connection

        self.connection_patch = patch.object(order, "get_connection", tracked_connection)
        self.connection_patch.start()
        self.addCleanup(self.connection_patch.stop)
        self.addCleanup(self.remove_test_orders)

    def remove_test_orders(self):
        # remove only orders created by this test
        if self.order_ids:
            connection = get_connection()
            try:
                cursor = connection.cursor()
                for order_id in self.order_ids:
                    cursor.execute("DELETE FROM orderproduct WHERE orderId = ?", order_id)
                    cursor.execute("DELETE FROM ordersummary WHERE orderId = ?", order_id)
                connection.commit()
            finally:
                connection.close()
        self.assertTrue(all(connection.closed for connection in self.connections))

    def add_product(self, product, **changes):
        product_id, name, price = product
        values = {"id": product_id, "name": name, "price": str(price)}
        values.update(changes)
        response = self.client.get("/addcart", query_string=values, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def submit(self, **changes):
        values = {"customerId": str(self.customer_id)}
        values.update(changes)
        return self.client.post("/order", data=values)

    def cart(self):
        with self.client.session_transaction() as session:
            return session.get("productList", {})

    def assert_no_saved_orders(self):
        connection = get_connection()
        try:
            cursor = connection.cursor()
            for order_id in self.order_ids:
                self.assertEqual(cursor.execute(
                    "SELECT COUNT(*) FROM ordersummary WHERE orderId = ?", order_id).fetchone()[0], 0)
                self.assertEqual(cursor.execute(
                    "SELECT COUNT(*) FROM orderproduct WHERE orderId = ?", order_id).fetchone()[0], 0)
        finally:
            connection.close()

    def test_search_cart_checkout_and_saved_order(self):
        product_id, name, price = self.products[0]
        response = self.client.get("/listprod", query_string={"productName": name})
        self.assertEqual(response.status_code, 200)
        links = re.findall(r'href="([^"]+)"', response.get_data(as_text=True))
        link = next(unescape(link) for link in links if f"id={product_id}&" in unescape(link))
        self.assertEqual(self.client.get(link, follow_redirects=True).status_code, 200)
        self.add_product(self.products[0])
        self.add_product(self.products[1])
        self.assertEqual(self.client.get("/checkout").status_code, 200)
        response = self.submit()
        self.assertEqual(response.status_code, 200)
        self.assertIn("placed successfully", response.get_data(as_text=True))
        self.assertFalse(self.cart())
        self.assertTrue(self.connections[-1].committed)

        connection = get_connection()
        try:
            cursor = connection.cursor()
            order_id = self.order_ids[-1]
            saved = cursor.execute(
                "SELECT customerId, totalAmount FROM ordersummary WHERE orderId = ?", order_id).fetchone()
            self.assertEqual(saved[0], self.customer_id)
            self.assertEqual(saved[1], price * 2 + self.products[1][2])
            items = cursor.execute(
                "SELECT productId, quantity, price FROM orderproduct WHERE orderId = ? "
                "ORDER BY productId", order_id).fetchall()
            self.assertEqual([tuple(item) for item in items],
                             [(product_id, 2, price), (self.products[1][0], 1, self.products[1][2])])
        finally:
            connection.close()
        history = self.client.get("/listorder")
        self.assertEqual(history.status_code, 200)
        self.assertIn(f"<td>{order_id}</td>", history.get_data(as_text=True))
        self.assertEqual(self.submit().status_code, 400)
        self.assertEqual(len(self.order_ids), 1)

    def test_changed_price_requires_confirmation_and_rechecks(self):
        self.add_product(self.products[0], price="0", name="<script>fake</script>")
        response = self.submit(confirm="1")
        self.assertIn("Prices updated", response.get_data(as_text=True))
        self.assertIn("Confirm Order", response.get_data(as_text=True))
        self.assertNotIn("<script>fake</script>", response.get_data(as_text=True))
        self.assertEqual(self.order_ids, [])
        self.assertEqual(Decimal(next(iter(self.cart().values()))["price"]), self.products[0][2])
        response = self.submit()
        self.assertIn("placed successfully", response.get_data(as_text=True))
        self.assertEqual(len(self.order_ids), 1)

    def test_invalid_customer_preserves_cart(self):
        self.add_product(self.products[0])
        original = self.cart()
        for value in ("", "0", "-1", "1.5", "2147483648", "1 OR 1=1", "2147483647"):
            with self.subTest(customer=value):
                self.assertEqual(self.submit(customerId=value).status_code, 400)
                self.assertEqual(self.cart(), original)
                self.assertEqual(self.order_ids, [])

    def test_empty_cart(self):
        response = self.submit()
        self.assertEqual(response.status_code, 400)
        self.assertIn("cart is empty", response.get_data(as_text=True))
        self.assertEqual(self.order_ids, [])

    def test_missing_product_preserves_cart(self):
        self.add_product((2147483647, "Missing product", Decimal("1.00")))
        original = self.cart()
        self.assertEqual(self.submit().status_code, 400)
        self.assertEqual(self.cart(), original)
        self.assertEqual(self.order_ids, [])

    def test_invalid_quantity_or_price_preserves_cart(self):
        for field, value in (("quantity", 0), ("quantity", -1), ("quantity", 1.5),
                             ("quantity", True), ("price", "NaN"), ("price", "bad")):
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

    def test_total_overflow_preserves_cart(self):
        self.add_product(self.products[0])
        with self.client.session_transaction() as session:
            cart = session["productList"]
            next(iter(cart.values()))["quantity"] = 2147483647
            session["productList"] = cart
        original = self.cart()
        self.assertEqual(self.submit().status_code, 400)
        self.assertEqual(self.cart(), original)
        self.assertEqual(self.order_ids, [])

    def test_second_item_failure_rolls_back_everything(self):
        self.add_product(self.products[0])
        self.add_product(self.products[1])
        original = self.cart()
        self.fail_on_item = 2
        with self.assertLogs(app.logger, level="ERROR"):
            response = self.submit()
        self.assertEqual(response.status_code, 500)
        self.assertEqual(len(self.order_ids), 1)
        self.assertTrue(self.connections[-1].rolled_back)
        self.assertFalse(self.connections[-1].committed)
        self.assertEqual(self.cart(), original)
        self.assert_no_saved_orders()

    def test_commit_failure_preserves_cart_and_rolls_back(self):
        self.add_product(self.products[0])
        original = self.cart()
        self.fail_commit = True
        with self.assertLogs(app.logger, level="ERROR"):
            response = self.submit()
        self.assertEqual(response.status_code, 500)
        self.assertEqual(self.cart(), original)
        self.assertTrue(self.connections[-1].rolled_back)
        self.assert_no_saved_orders()


if __name__ == "__main__":
    unittest.main()
