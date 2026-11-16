"""Lab 8 images, login, customer, report and shipment checks."""

import re
import unittest
from collections import defaultdict
from decimal import Decimal
from unittest.mock import patch
from urllib.parse import urlparse

from app import app
from routes import admin, customer, ship
from support import DatabaseTest, Page, read_rows


class Lab8Tests(DatabaseTest):
    def login(self):
        username, password = read_rows("SELECT userid, password FROM customer WHERE customerId = ?",
                                       [self.customer_id])[0]
        response = self.client.post("/validateLogin", data={"username": username, "password": password})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, "/")
        return username, password

    def test_product_details_and_both_image_sources(self):
        products = read_rows("SELECT TOP 1 productId, productName, productPrice, productDesc, "
                             "productImageURL, productImage FROM product "
                             "WHERE productImageURL IS NOT NULL AND productImage IS NOT NULL ORDER BY productId")
        self.assertTrue(products, "Load a product with both image methods before running the tests")
        product_id, name, price, description, image_url, image_data = products[0]
        listing = self.client.get("/listprod", query_string={"productName": name})
        self.assertIn(f"/product?id={product_id}", Page(listing).links)
        response = self.client.get("/product", query_string={"id": product_id})
        self.assertEqual(response.status_code, 200)
        page = Page(response)
        self.assertIn(name, page.text)
        if description:
            self.assertIn(" ".join(description.split()), page.text)
        file_url = image_url if image_url.startswith(("http://", "https://", "/")) else "/static/" + image_url
        binary_url = f"/displayImage?id={product_id}"
        self.assertIn(file_url, page.images)
        self.assertIn(binary_url, page.images)
        # local URL images can be checked without depending on an outside server
        if file_url.startswith("/") and not file_url.startswith("//"):
            file_response = self.client.get(file_url)
            self.assertEqual(file_response.status_code, 200)
            self.assertTrue(file_response.mimetype.startswith("image/"))
        image = self.client.get(binary_url)
        self.assertEqual(image.status_code, 200)
        self.assertEqual(image.data, bytes(image_data))
        expected_type = "image/png" if bytes(image_data).startswith(b"\x89PNG") else "image/jpeg"
        self.assertEqual(image.mimetype, expected_type)
        self.assertIn("/listprod", page.links)
        cart_link = next(link for link in page.links if urlparse(link).path == "/addcart")
        self.assertEqual(self.client.get(cart_link).status_code, 302)
        with self.client.session_transaction() as session:
            item = session["productList"][str(product_id)]
            self.assertEqual(item["name"], name)
            self.assertEqual(Decimal(str(item["price"])), price)

    def test_invalid_products_and_missing_images(self):
        product_id, name, price = self.create_product("no image", Decimal("1.23"))
        self.assertFalse(Page(self.client.get(f"/product?id={product_id}")).images)
        self.assertEqual(self.client.get(f"/displayImage?id={product_id}").status_code, 404)
        for route in ("/product", "/displayImage"):
            for value in ("", "abc", "0", "-1", "1.5", "2147483648", "1 OR 1=1"):
                with self.subTest(route=route, value=value):
                    self.assertEqual(self.client.get(route, query_string={"id": value}).status_code, 400)
            self.assertEqual(self.client.get(route, query_string={"id": 2147483647}).status_code, 404)

    def test_login_logout_preserve_cart(self):
        cart = {"1": {"id": "1", "name": "test item", "price": 2, "quantity": 3}}
        with self.client.session_transaction() as session:
            session["productList"] = cart
            session["loginMessage"] = "old message"
        username, password = self.login()
        with self.client.session_transaction() as session:
            self.assertEqual(session["authenticatedUser"], username)
            self.assertEqual(session["productList"], cart)
            self.assertNotIn("loginMessage", session)
            self.assertNotIn("password", session)
        self.assertIn(username, Page(self.client.get("/")).text)
        self.client.get("/logout")
        with self.client.session_transaction() as session:
            self.assertNotIn("authenticatedUser", session)
            self.assertEqual(session["productList"], cart)
        for path in ("/customer", "/admin"):
            self.assertEqual(urlparse(self.client.get(path).location).path, "/login")

    def test_invalid_and_injection_logins_clear_identity(self):
        username, password = self.login()
        for user, secret in ((username, "wrong_92831"), ("", password), (username, ""),
                             ("' OR 1=1 --", "x"), (username, "' OR 1=1 --")):
            with self.subTest(username=user):
                with self.client.session_transaction() as session:
                    session["authenticatedUser"] = username
                response = self.client.post("/validateLogin", data={"username": user, "password": secret})
                self.assertEqual(response.status_code, 302)
                self.assertEqual(urlparse(response.location).path, "/login")
                with self.client.session_transaction() as session:
                    self.assertNotIn("authenticatedUser", session)
                    self.assertTrue(session.get("loginMessage"))

    def test_protected_routes_check_login_before_query(self):
        for module, path in ((customer, "/customer"), (admin, "/admin")):
            with patch.object(module, "get_connection") as connect:
                response = self.client.get(path)
                self.assertEqual(response.status_code, 302)
                self.assertEqual(urlparse(response.location).path, "/login")
                connect.assert_not_called()

    def test_customer_details_ignore_url_identity(self):
        username, password = self.login()
        response = self.client.get("/customer")
        self.assertEqual(response.status_code, 200)
        text = Page(response).text
        values = read_rows("SELECT firstName, lastName, email, phonenum, address, city, state, "
                           "postalCode, country, userid FROM customer WHERE customerId = ?", [self.customer_id])[0]
        for value in values:
            if value:
                self.assertIn(" ".join(value.split()), text)
        self.assertNotIn(password, text)
        for args in ({"customerId": 2147483647}, {"id": 2147483647}, {"userid": "another user"}):
            self.assertEqual(Page(self.client.get("/customer", query_string=args)).text, text)
        with self.client.session_transaction() as session:
            session["authenticatedUser"] = self.token
        self.assertEqual(self.client.get("/customer").status_code, 404)

    def test_daily_sales_group_by_date_and_sort(self):
        product_id, name, price = self.create_product("sales", Decimal("2.34"))
        for date, quantity in (("2001-02-04 09:00:00", 3), ("2001-02-03 10:00:00", 1),
                               ("2001-02-03 17:00:00", 2)):
            self.create_order([(product_id, quantity, price)], date)
        totals = defaultdict(lambda: Decimal("0"))
        for timestamp, amount in read_rows("SELECT orderDate, totalAmount FROM ordersummary"):
            totals[timestamp.date()] += amount
        self.login()
        response = self.client.get("/admin")
        self.assertEqual(response.status_code, 200)
        text = Page(response).text
        positions = []
        for day, total in sorted(totals.items()):
            self.assertEqual(text.count(str(day)), 1)
            self.assertRegex(text, re.escape(str(day)) + r"\s+\$?" + re.escape(f"{total:.2f}"))
            positions.append(text.index(str(day)))
        self.assertEqual(positions, sorted(positions))

    def shipment_order(self, second_stock=3):
        self.first = self.create_product("stock A", Decimal("2.00"), stock=4)
        self.second = self.create_product("stock B", Decimal("3.00"), stock=second_stock)
        self.ship_order_id = self.create_order([(self.first[0], 2, self.first[2]),
                                                (self.second[0], 1, self.second[2])])
        self.original_stock = self.stock()
        self.original_shipments = read_rows("SELECT * FROM shipment ORDER BY shipmentId")

    def stock(self):
        return read_rows("SELECT productId, quantity FROM productinventory "
                         "WHERE warehouseId = 1 AND productId IN (?, ?) ORDER BY productId",
                         [self.first[0], self.second[0]])

    def test_successful_shipment_commits_all_items(self):
        self.shipment_order()
        self.watch(ship, "shipment")
        response = self.client.get("/ship", query_string={"orderId": self.ship_order_id})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.connections[-1].committed)
        self.assertEqual(self.stock(), [(self.first[0], 2), (self.second[0], 2)])
        self.assertEqual(len(self.shipment_ids), 1)
        self.assertEqual(read_rows("SELECT shipmentDesc, warehouseId FROM shipment WHERE shipmentId = ?",
                                   [self.shipment_ids[0]]), [(f"Order {self.ship_order_id}", 1)])

    def test_insufficient_second_item_rolls_back(self):
        self.shipment_order(second_stock=0)
        self.watch(ship, "shipment")
        self.assert_shipment_rollback(400)

    def test_second_update_error_rolls_back(self):
        self.shipment_order()
        self.watch(ship, "shipment", fail_sql="UPDATE productinventory", fail_at=2)
        with self.assertLogs(app.logger, level="ERROR"):
            self.assert_shipment_rollback(500)
        self.assertEqual(self.connections[-1].matches, 2)

    def test_shipment_commit_error_rolls_back(self):
        self.shipment_order()
        self.watch(ship, "shipment", fail_commit=True)
        with self.assertLogs(app.logger, level="ERROR"):
            self.assert_shipment_rollback(500)

    def assert_shipment_rollback(self, status):
        response = self.client.get("/ship", query_string={"orderId": self.ship_order_id})
        self.assertEqual(response.status_code, status)
        self.assertTrue(self.connections[-1].rolled_back)
        self.assertFalse(self.connections[-1].committed)
        self.assertEqual(len(self.shipment_ids), 1)
        self.assertEqual(self.stock(), self.original_stock)
        self.assertEqual(read_rows("SELECT * FROM shipment ORDER BY shipmentId"), self.original_shipments)

    def test_invalid_and_missing_shipment_orders(self):
        before = read_rows("SELECT * FROM shipment ORDER BY shipmentId")
        self.watch(ship, "shipment")
        for value in ("", "abc", "0", "-1", "1.5", "2147483648", "1 OR 1=1", "2147483647"):
            with self.subTest(order_id=value):
                self.assertEqual(self.client.get("/ship", query_string={"orderId": value}).status_code, 400)
        self.assertEqual(self.shipment_ids, [])
        self.assertEqual(read_rows("SELECT * FROM shipment ORDER BY shipmentId"), before)


if __name__ == "__main__":
    unittest.main()
