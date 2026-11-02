"""Question 1 (10 marks): list all orders and their ordered products."""

from flask import Blueprint, current_app
from db import get_connection
from html_utils import escape_html, format_currency, html_page

bp = Blueprint("listorder", __name__)


@bp.get("/listorder")
def list_orders():
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()

        sql = """
            SELECT o.orderId, o.orderDate, o.customerId,
                   c.firstName, c.lastName, o.totalAmount
            FROM ordersummary o
            LEFT JOIN customer c ON o.customerId = c.customerId
            ORDER BY o.orderId"""
        # get all orders first since we reuse the cursor below
        orders = cursor.execute(sql).fetchall()

        output = ["<h1>Order List</h1>"]

        if not orders:
            output.append("<p>No orders yet</p>")

        for order_id, order_date, customer_id, first, last, total in orders:
            customer_name = f"{first or ''} {last or ''}".strip()

            output.append(
                '<table border="1">'
                "<tr><th>Order ID</th><th>Date</th><th>Customer ID</th>"
                "<th>Customer</th><th>Total</th></tr>"
                f"<tr><td>{order_id}</td>"
                f"<td>{escape_html(order_date)}</td>"
                f"<td>{escape_html(customer_id)}</td>"
                f"<td>{escape_html(customer_name)}</td>"
                f"<td>{format_currency(total)}</td></tr>"
                "</table>")

            # use the price from the order not the current product price
            sql = """
                SELECT p.productId, p.productName, op.quantity, op.price
                FROM orderproduct op
                JOIN product p ON op.productId = p.productId
                WHERE op.orderId = ?
                ORDER BY p.productId"""
            items = cursor.execute(sql, order_id).fetchall()

            output.append("<h3>Products</h3>")

            if not items:
                output.append("<p>No items</p>")
            else:
                output.append(
                    '<table border="1">'
                    "<tr><th>Product ID</th><th>Name</th><th>Quantity</th>"
                    "<th>Price</th><th>Item total</th></tr>")

                for product_id, product_name, quantity, price in items:
                    output.append(
                        f"<tr><td>{product_id}</td>"
                        f"<td>{escape_html(product_name)}</td>"
                        f"<td>{quantity}</td>"
                        f"<td>{format_currency(price)}</td>"
                        f"<td>{format_currency(quantity * price)}</td></tr>")

                output.append("</table>")

            output.append("<hr>")

        return html_page("YOUR NAME Grocery Order List", "".join(output))
    except Exception:
        # Log the actual error in the terminal; do not display credentials to users.
        current_app.logger.exception("Unable to list orders")
        return html_page("Order List Error", "<h1>Unable to retrieve orders.</h1>"), 500
    finally:
        if connection is not None:
            connection.close()
