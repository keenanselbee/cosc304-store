"""Shared database cleanup and response parsing for the lab tests."""

import unittest
from html.parser import HTMLParser
from unittest.mock import patch
from uuid import uuid4

from app import app
from db import get_connection


def read_rows(query, parameters=()):
    connection = get_connection()
    try:
        return [tuple(row) for row in connection.cursor().execute(query, parameters)]
    finally:
        connection.close()


class Page(HTMLParser):
    def __init__(self, response):
        super().__init__()
        self.links = []
        self.images = []
        self.words = []
        self.feed(response.get_data(as_text=True))
        self.text = " ".join(self.words)

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if tag == "a":
            self.links.append(attributes.get("href", ""))
        if tag == "img":
            self.images.append(attributes.get("src", ""))

    def handle_data(self, text):
        self.words.extend(text.split())


class TrackedConnection:
    def __init__(self, ids, table, fail_sql=None, fail_at=1, fail_commit=False):
        self.connection = get_connection()
        self.ids, self.table = ids, table
        self.fail_sql, self.fail_at, self.fail_commit = fail_sql, fail_at, fail_commit
        self.matches = 0
        self.committed = self.rolled_back = self.closed = False

    def cursor(self):
        return TrackedCursor(self, self.connection.cursor())

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


class TrackedCursor:
    def __init__(self, connection, cursor):
        self.connection, self.cursor = connection, cursor
        self.capture_id = False

    def execute(self, query, *parameters):
        connection = self.connection
        if connection.fail_sql and query.lstrip().startswith(connection.fail_sql):
            connection.matches += 1
            if connection.matches == connection.fail_at:
                raise RuntimeError("Simulated database write failure")
        self.capture_id = query.lstrip().startswith(f"INSERT INTO {connection.table}")
        self.cursor.execute(query, *parameters)
        return self

    def fetchone(self):
        row = self.cursor.fetchone()
        if self.capture_id and row is not None:
            self.connection.ids.append(row[0])
            self.capture_id = False
        return row

    def __getattr__(self, name):
        return getattr(self.cursor, name)

    def __iter__(self):
        return iter(self.cursor)


class DatabaseTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.token = uuid4().hex[:12]
        self.order_ids, self.product_ids, self.shipment_ids = [], [], []
        self.connections = []
        self.addCleanup(self.remove_test_data)
        self.customer_id = read_rows("SELECT TOP 1 customerId FROM customer ORDER BY customerId")[0][0]

    def create_product(self, suffix, price, stock=None):
        name = f"Test {self.token} {suffix}"
        connection = get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO product (productName, productPrice) "
                           "OUTPUT INSERTED.productId VALUES (?, ?)", [name, price])
            product_id = cursor.fetchone()[0]
            self.product_ids.append(product_id)
            if stock is not None:
                cursor.execute("INSERT INTO productinventory (productId, warehouseId, quantity, price) "
                               "VALUES (?, 1, ?, ?)", [product_id, stock, price])
            connection.commit()
            return product_id, name, price
        finally:
            connection.close()

    def create_order(self, items, date="2001-02-03 10:00:00"):
        connection = get_connection()
        try:
            cursor = connection.cursor()
            total = sum(quantity * price for product_id, quantity, price in items)
            cursor.execute("INSERT INTO ordersummary (customerId, orderDate, totalAmount) "
                           "OUTPUT INSERTED.orderId VALUES (?, ?, ?)", [self.customer_id, date, total])
            order_id = cursor.fetchone()[0]
            self.order_ids.append(order_id)
            for product_id, quantity, price in items:
                cursor.execute("INSERT INTO orderproduct (orderId, productId, quantity, price) "
                               "VALUES (?, ?, ?, ?)", [order_id, product_id, quantity, price])
            connection.commit()
            return order_id
        finally:
            connection.close()

    def watch(self, module, table, **failures):
        ids = self.order_ids if table == "ordersummary" else self.shipment_ids

        def connect():
            connection = TrackedConnection(ids, table, **failures)
            self.connections.append(connection)
            return connection

        replacement = patch.object(module, "get_connection", connect)
        replacement.start()
        self.addCleanup(replacement.stop)

    def remove_test_data(self):
        # release any failed route connection before removing our own records
        unclosed = [connection for connection in self.connections if not connection.closed]
        for connection in unclosed:
            connection.rollback()
            connection.close()
        connection = get_connection()
        try:
            cursor = connection.cursor()
            for shipment_id in self.shipment_ids:
                cursor.execute("DELETE FROM shipment WHERE shipmentId = ?", [shipment_id])
            for order_id in self.order_ids:
                cursor.execute("DELETE FROM orderproduct WHERE orderId = ?", [order_id])
                cursor.execute("DELETE FROM ordersummary WHERE orderId = ?", [order_id])
            for product_id in self.product_ids:
                cursor.execute("DELETE FROM productinventory WHERE productId = ?", [product_id])
                cursor.execute("DELETE FROM product WHERE productId = ?", [product_id])
            connection.commit()
        finally:
            connection.close()
        self.assertFalse(unclosed, "A route left its database connection open")
