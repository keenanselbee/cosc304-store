"""Lab 8 TODO: process one order as an all-or-nothing shipment."""

from flask import Blueprint, current_app, request
from db import get_connection
from html_utils import escape_html, html_page

bp = Blueprint("ship", __name__)


@bp.get("/ship")
def ship_order():
    raw_order_id = request.args.get("orderId", "")

    # --------------------------------
    # check the order id
    navigation = '<p><a href="/">Main Page</a></p>'
    try:
        order_id = int(raw_order_id)
        if order_id <= 0 or order_id > 2147483647:
            raise ValueError()
    except ValueError:
        return html_page("Shipment Processing", "<p>Invalid order ID</p>" + navigation), 400

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = """SELECT productId, quantity
                    FROM orderproduct
                    WHERE orderId = ?
                    ORDER BY productId"""
        cursor.execute(query, [order_id])
        products = cursor.fetchall()
        if not products:
            raise ValueError("Order not found or has no items")

        # keep the shipment and stock changes in one transaction
        query = """INSERT INTO shipment (shipmentDate, shipmentDesc, warehouseId)
                   OUTPUT INSERTED.shipmentId VALUES (GETDATE(), ?, 1)"""
        cursor.execute(query, [f"Order {order_id}"])
        shipment_id = cursor.fetchone()[0]

        rows = []
        for product_id, quantity in products:
            if quantity is None or quantity <= 0:
                raise ValueError(f"Invalid quantity for product {product_id}")

            # only subtract stock when enough is available
            query = """UPDATE productinventory SET quantity = quantity - ?
                       WHERE productId = ? AND warehouseId = 1 AND quantity >= ?"""
            cursor.execute(query, [quantity, product_id, quantity])
            if cursor.rowcount != 1:
                raise ValueError(f"Not enough stock for product {product_id} in warehouse 1")

            rows.append(f"<tr><td>{product_id}</td><td>{quantity}</td></tr>")

        output = (f"<h1>Order {order_id} shipped</h1>"
                  f"<p>Shipment {shipment_id} from warehouse 1</p>"
                  '<table border="1"><tr><th>Product ID</th><th>Quantity shipped</th></tr>'
                  + "".join(rows) + "</table>" + navigation)
        connection.commit()
        return html_page("Shipment Processing", output)
    except ValueError as error:
        if connection is not None:
            connection.rollback()
        return html_page("Shipment Processing",
                         f"<p>{escape_html(error)}</p><p>No shipment changes saved</p>" + navigation), 400
    except Exception:
        if connection is not None:
            connection.rollback()
        current_app.logger.exception("Unable to process shipment")
        return html_page("Shipment Processing",
                         "<p>Unable to process shipment</p>" + navigation), 500
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
    # --------------------------------
