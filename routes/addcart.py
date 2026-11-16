"""Provided route: add a product from the search results to the session cart."""

import re
from decimal import Decimal, InvalidOperation

from flask import Blueprint, redirect, request, session, url_for, current_app
from db import get_connection
from html_utils import html_page

bp = Blueprint("addcart", __name__)


@bp.get("/addcart")
def add_to_cart():
    product_id = request.args.get("id", "")
    name = request.args.get("name", "")
    raw_price = request.args.get("price", "")
    try:
        price = Decimal(raw_price)
        valid_price = price.is_finite() and 0 <= price <= 99999999.99
    except (InvalidOperation, ValueError):
        price, valid_price = None, False

    if not re.fullmatch(r"[1-9][0-9]{0,9}", product_id) or int(product_id) > 2147483647:
        return ('Invalid product information. <a href="/listprod">Return to products</a>', 400)
    if not name.strip() or not valid_price:
        return ('Invalid product information. <a href="/listprod">Return to products</a>', 400)

    # keep retired gear out of new carts
    connection = None
    try:
        connection = get_connection()
        row = connection.cursor().execute(
            "SELECT c.categoryName FROM product p JOIN category c ON p.categoryId = c.categoryId "
            "WHERE p.productId = ?", [int(product_id)]).fetchone()
        if row is not None and row[0] == "Past Stock":
            return html_page("Past Stock", "<h1>This item is no longer offered</h1>"
                             '<p><a href="/listprod">Browse current gear</a></p>'), 400
    except Exception:
        current_app.logger.exception("Unable to check product availability")
        return html_page("Cart Error", "<h1>Unable to add this item</h1>"
                         '<p><a href="/listprod">Return to products</a></p>'), 500
    finally:
        if connection is not None:
            connection.close()

    # Flask stores the cart in a signed browser session cookie. Reassign the
    # mapping so Flask persists changes to nested session values.
    cart = dict(session.get("productList", {}))
    if product_id in cart:
        product = dict(cart[product_id])
        product["quantity"] = int(product["quantity"]) + 1
    else:
        product = {"id": product_id, "name": name, "price": float(price), "quantity": 1}
    cart[product_id] = product
    session["productList"] = cart
    return redirect(url_for("showcart.show_cart"))
