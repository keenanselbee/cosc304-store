"""Question 2 (20 marks): validate and save a completed order."""

from flask import Blueprint, request, session, current_app
from pyodbc import connect
from db import get_connection
from html_utils import escape_html, format_currency, html_page

bp = Blueprint("order", __name__)


@bp.post("/order")
def place_order():
    customer_id = request.form.get("customerId", "")
    products = list(session.get("productList", {}).values())
    connection = None

    try:
        # TODO (Q2): Validate that customer_id is a positive integer and exists
        #       in the customer table. Show an error if not valid.
        if not str(customer_id).isdigit() or int(customer_id) <= 0:
            return html_page("Order Error", "<h1>Invalid customer id. Go back to the previous page and try again.</h1>")

        # TODO: Show an error if the products list is empty.
        if not products:
            return html_page("Order Error", "<h1>Your shopping cart is empty!</h1>")
        # TODO: Open a connection to the orders database.
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT customerId FROM customer WHERE customerId = ?", 
            int(customer_id),
        )



        # TODO: INSERT ordersummary with the customer ID and order date.
        #       Use a parameterized INSERT and return the generated orderId.
        #       In SQL Server, INSERT ... OUTPUT INSERTED.orderId ... works.
        cursor.execute(
            "INSERT INTO ordersummary (customerId, orderDate)" "OUTPUT INSERTED.orderId VALUES (?, GETDATE())", int(customer_id))
        order_id = cursor.fetchone()[0]
        # TODO: Loop through products; entries have id, name, price, quantity.
        #       INSERT each item into orderproduct, using ? placeholders.
        
        total = 0
        for item in products:
            price = float(item["price"])
            quantity = int(item["quantity"])
            total += price * quantity
            cursor.execute(
                "INSERT INTO orderproduct (orderId, productId, quantity, price)"
                "VALUES (?, ?, ?, ?)",
                order_id, int(item["id"]), quantity, price,
            )
        # TODO: UPDATE ordersummary.totalAmount for the order.
        #       Commit only when all statements succeed; roll back on failure.
        cursor.execute(
            "UPDATE ordersummary SET totalAmount = ? WHERE orderId = ?",
            total, order_id,
        )
        connection.commit()
        # TODO: Display order ID, purchased products, and total amount.
        rows = ""
        for item in products:
            line = float(item["price"]) * int(item["quantity"])
            rows += (
                f"<tr><td>{escape_html(item['name'])}</td>"
                f"<td>{escape_html(item['quantity'])}</td>"
                f"<td>{format_currency(item['price'])}</td>"
                f"<td>{format_currency(line)}</td></tr>"
            )

        session.pop("productList", None)

        return html_page(
            "Order Complete",
            "<h1>Order complete</h1>"
            f"<p>Order id: {escape_html(order_id)}</p>"
            "<table border='1'><tr><th>Product</th><th>Quantity</th>"
            "<th>Price</th><th>Subtotal</th></tr>"
            + rows
            + f"<tr><td colspan='3'>Total</td><td>{format_currency(total)}</td></tr>"
            "</table>",
        )
        # TODO: Clear session['productList'] only after the order is committed.
        # Use escape_html() for HTML text and format_currency() for prices.
        return html_page("YOUR NAME Grocery Order Processing",
                         "<h1>Order Processing</h1><p>TODO: implement Question 2.</p>")
    except Exception:
        current_app.logger.exception("Unable to process order")
        # TODO (Q2): Roll back any uncommitted inserts on a failure.
        if connection is not None:
            connection.rollback()
        return html_page("Order Processing Error",
                         "<h1>Unable to process the order.</h1>"), 500
    finally:
        # TODO (Q2): Close the connection if it was opened.
        if connection is not None:
            connection.close()
