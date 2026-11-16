"""Provided route: display the current session's shopping cart."""

from decimal import Decimal
from flask import Blueprint, session, current_app, url_for
from db import get_connection
from html_utils import escape_html, format_currency, html_page, image_source

bp = Blueprint("showcart", __name__)


@bp.get("/showcart")
def show_cart():
    products = list(session.get("productList", {}).values())
    if not products:
        return html_page("Your Cart", '<div class="empty-message"><h1>Your cart is empty</h1>'
                         '<p class="gruk-aside">Nothing? You fighting dragon with manners?</p>'
                         '<a class="button" href="/listprod">Continue Shopping</a></div>')

    # pictures are optional and do not change cart prices
    images = {}
    connection = None
    try:
        connection = get_connection()
        ids = [int(item["id"]) for item in products]
        placeholders = ",".join("?" for _ in ids)
        rows = connection.cursor().execute(
            "SELECT productId, productImageURL FROM product WHERE productId IN (" + placeholders + ")", ids)
        images = {str(row[0]): image_source(row[1]) for row in rows}
    except Exception:
        current_app.logger.exception("Unable to load cart pictures")
    finally:
        if connection is not None:
            connection.close()

    total = Decimal("0.00")
    rows = []
    for product in products:
        subtotal = Decimal(str(product["price"])) * int(product["quantity"])
        total += subtotal
        picture = images.get(str(product["id"]))
        artwork = f'<img src="{escape_html(picture)}" alt="">' if picture else ""
        link = url_for("product.product_details", id=product["id"])
        rows.append(f'<tr><td><div class="cart-product">{artwork}<div>'
                    f'<a href="{escape_html(link)}">{escape_html(product["name"])}</a>'
                    f'<small>Product ID: {escape_html(product["id"])}</small></div></div></td>'
                    f"<td>{int(product['quantity'])}</td>"
                    f"<td>{format_currency(product['price'])}</td>"
                    f"<td>{format_currency(subtotal)}</td></tr>")

    return html_page("Your Cart", "<h1>Your Cart</h1>"
                     '<p class="gruk-aside">Good pile. Could be bigger pile.</p>'
                     '<table class="cart-table"><tr><th>Product</th>'
                     '<th>Quantity</th><th>Price</th><th>Subtotal</th></tr>'
                     + "".join(rows)
                     + '<tr class="cart-total"><th colspan="3">Order total</th>'
                     + f"<td>{format_currency(total)}</td></tr></table>"
                     + '<div class="cart-actions"><a href="/listprod">Continue Shopping</a>'
                     + '<a class="button" href="/checkout">Checkout</a></div>')
