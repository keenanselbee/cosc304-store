"""Lab 8 TODO: process one order as an all-or-nothing shipment."""

from flask import Blueprint, request
from db import get_connection
from html_utils import escape_html, html_page

bp = Blueprint("ship", __name__)


@bp.get("/ship")
def ship_order():
    raw_order_id = request.args.get("orderId", "")

    # TODO: Validate orderId and retrieve ALL orderproduct rows for the order.
    # TODO: Open one connection (get_connection defaults to autocommit=False).
    # TODO: Create a shipment record for warehouseId = 1.
    # TODO: For each ordered product, verify warehouse 1 has enough inventory
    #       and update productinventory by subtracting the ordered quantity.
    # TODO: Commit the transaction only if ALL items can be shipped.
    # TODO: On any error, rollback() all changes, including the shipment row
    #       and any preceding inventory updates; close the connection.
    # TODO: Display a success or failure message and a Main Page link.
    return html_page("Shipment Processing", """
        <h1>Process Shipment</h1>
        <p>TODO: process the order transactionally.</p>
        <p><a href="/">Main Page</a></p>
    """)
