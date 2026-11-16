"""Question 2 (10 marks): display/search products and provide cart links."""

from flask import Blueprint, request, current_app, render_template
from db import get_connection
from html_utils import format_currency, html_page, image_source

bp = Blueprint("listprod", __name__)


@bp.get("/listprod")
def list_products():
    name = request.args.get("productName", "")
    category = request.args.get("category", "")
    products = []
    error = None
    status = 200
    connection = None
    try:
        if category not in ("", "Weapons", "Armour", "Potions"):
            return html_page("Product Search", "<h1>Unknown category</h1>"
                             '<p><a href="/listprod">Browse all gear</a></p>'), 400
        connection = get_connection()
        cursor = connection.cursor()
        sql = """SELECT p.productId, p.productName, p.productPrice, p.productImageURL, c.categoryName
                 FROM product p JOIN category c ON p.categoryId = c.categoryId
                 WHERE c.categoryName IN (?, ?, ?)"""
        parameters = ["Weapons", "Armour", "Potions"]
        if name.strip():
            sql += " AND p.productName LIKE ?"
            parameters.append(f"%{name}%")
        if category:
            sql += " AND c.categoryName = ?"
            parameters.append(category)
        cursor.execute(sql + " ORDER BY p.productId", parameters)
        products = cursor.fetchall()
    except Exception:
        current_app.logger.exception("Unable to list products")
        error = "Unable to search products"
        status = 500
    finally:
        if connection is not None:
            connection.close()

    # the template links names to details and uses the actual cart values
    body = render_template("shop.html", name=name, category=category, products=products,
                           error=error, format_currency=format_currency, image_source=image_source)
    return html_page("Shop", body, shop=True), status
