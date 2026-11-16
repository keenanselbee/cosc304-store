"""Question 2 (20 marks): validate and save a completed order."""

import re
from decimal import Decimal, InvalidOperation

from flask import Blueprint, request, session, current_app, url_for
from db import get_connection
from html_utils import escape_html, format_currency, html_page

bp = Blueprint("order", __name__)


@bp.post("/order")
def place_order():
    customer_id = request.form.get("customerId", "").strip()
    connection = None
    cart_link = f'<p><a href="{url_for("showcart.show_cart")}">Return to Shopping Cart</a></p>'

    try:
        # check the customer and cart
        if not re.fullmatch(r"[1-9][0-9]{0,9}", customer_id) or int(customer_id) > 2147483647:
            raise ValueError("Enter a valid customer ID")
        customer_id = int(customer_id)
        cart = session.get("productList", {})
        if not cart:
            raise ValueError("Your cart is empty")
        if not isinstance(cart, dict):
            raise ValueError("Something is wrong with your cart")

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT customerId FROM customer WHERE customerId = ?", customer_id)
        if cursor.fetchone() is None:
            raise ValueError("Customer ID not found")

        # use current database prices before saving the order
        products = []
        product_ids = set()
        prices_changed = False
        total = Decimal("0.00")
        for item in cart.values():
            if not isinstance(item, dict):
                raise ValueError("Invalid item in your cart")
            product_id = str(item.get("id", ""))
            quantity = str(item.get("quantity", ""))
            if not re.fullmatch(r"[1-9][0-9]{0,9}", product_id) or int(product_id) > 2147483647:
                raise ValueError("Invalid product ID")
            if not re.fullmatch(r"[1-9][0-9]{0,9}", quantity) or int(quantity) > 2147483647:
                raise ValueError("Quantity must be a whole number above 0")
            quantity = int(quantity)
            if product_id in product_ids:
                raise ValueError("This product appears twice in your cart")
            product_ids.add(product_id)
            try:
                cart_price = Decimal(str(item.get("price", "")))
            except InvalidOperation:
                raise ValueError("Invalid item price") from None
            if not cart_price.is_finite() or not 0 <= cart_price <= Decimal("99999999.99"):
                raise ValueError("Invalid item price")

            cursor.execute("SELECT productName, productPrice FROM product WHERE productId = ?",
                           int(product_id))
            product = cursor.fetchone()
            if product is None:
                raise ValueError(f"Product {product_id} was not found")
            name, price = product
            if price is None or price < 0:
                raise ValueError(f"Invalid price for product {product_id}")
            prices_changed = prices_changed or cart_price != price
            total += price * quantity
            products.append({"id": product_id, "name": name, "price": str(price), "quantity": quantity})
        if total > Decimal("99999999.99"):
            raise ValueError("Order total is too large try fewer items")

        # reuse the item table for price review and confirmation
        rows = ""
        for item in products:
            line = Decimal(item["price"]) * item["quantity"]
            rows += (
                f"<tr><td>{escape_html(item['name'])}</td>"
                f"<td>{escape_html(item['quantity'])}</td>"
                f"<td>{format_currency(item['price'])}</td>"
                f"<td>{format_currency(line)}</td></tr>")
        table = ("<table border='1'><tr><th>Product</th><th>Quantity</th>"
                 "<th>Price</th><th>Subtotal</th></tr>" + rows
                 + f"<tr><td colspan='3'>Total</td><td>{format_currency(total)}</td></tr></table>")

        if prices_changed:
            connection.rollback()
            session["productList"] = {item["id"]: item for item in products}
            return html_page(
                "Confirm Updated Prices", "<h1>Prices updated</h1>"
                "<p>Prices have changed check the new total before confirming</p>"
                + table + f'<form method="post" action="{url_for("order.place_order")}">'
                + f'<input type="hidden" name="customerId" value="{customer_id}">'
                + '<button type="submit">Confirm Order</button></form>' + cart_link)

        # save the order and its items in one transaction
        cursor.execute("INSERT INTO ordersummary (customerId, orderDate, totalAmount) "
                       "OUTPUT INSERTED.orderId VALUES (?, GETDATE(), 0)", customer_id)
        order_id = cursor.fetchone()[0]
        for item in products:
            cursor.execute("INSERT INTO orderproduct (orderId, productId, quantity, price) "
                           "VALUES (?, ?, ?, ?)",
                           order_id, int(item["id"]), item["quantity"], Decimal(item["price"]))

        # update the total after saving the items
        cursor.execute("UPDATE ordersummary SET totalAmount = ? WHERE orderId = ?", total, order_id)
        confirmation = html_page(
            "Order Complete", "<h1>Order complete</h1>"
            f"<p>Order {order_id} placed successfully.</p>" + table
            + f'<p><a href="{url_for("listorder.list_orders")}">View Orders</a></p>'
            + f'<p><a href="{url_for("listprod.list_products")}">Continue Shopping</a></p>')
        connection.commit()
        session.pop("productList", None)
        return confirmation
    except ValueError as error:
        if connection is not None:
            connection.rollback()
        return html_page("Order Error", "<h1>Unable to place order</h1>"
                         f"<p>{escape_html(error)}</p>" + cart_link), 400
    except Exception:
        current_app.logger.exception("Unable to process order")
        if connection is not None:
            connection.rollback()
        return html_page("Order Processing Error",
                         "<h1>Unable to process the order.</h1>"
                         "<p>Order failed your cart has been kept</p>" + cart_link), 500
    finally:
        if connection is not None:
            connection.close()
