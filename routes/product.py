"""Lab 8 product details with URL and database images."""

from flask import Blueprint, current_app, request, url_for, render_template
from db import get_connection
from html_utils import escape_html, format_currency, html_page, image_source

bp = Blueprint("product", __name__)


@bp.get("/product")
def product_details():
    product_id_text = request.args.get("id", "")

    # --------------------------------

    shopping_link = url_for("listprod.list_products")
    navigation = (f'<p><a href="{escape_html(shopping_link)}">Continue Shopping</a></p>')

    try:
        product_id = int(product_id_text)
        if product_id <= 0 or product_id > 2147483647:
            raise ValueError()
    except ValueError:
        return html_page("Product Details", "<p>Invalid product ID</p>" + navigation), 400

    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = """SELECT p.productId, p.productName, p.productPrice, p.productDesc,
                        p.productImageURL, p.productImage, c.categoryName
                    FROM product p JOIN category c ON p.categoryId = c.categoryId
                    WHERE p.productId = ?"""
        cursor.execute(query, [product_id])
        product = cursor.fetchone()

        if product is None:
            return html_page("Product Details", "<p>Product not found</p>" + navigation), 404

        product_id, name, price, description, image_url, image_data, category = product
        output = render_template("product.html", product_id=product_id, name=name, price=price,
                                 description=description, image_url=image_source(image_url),
                                 has_database_image=image_data is not None, category=category,
                                 format_currency=format_currency)
        return html_page(name, output)
    except Exception:
        current_app.logger.exception("Unable to load product")
        return html_page("Product Details", "<p>Unable to load product</p>" + navigation), 500
    finally:
        if connection is not None:
            connection.close()

    # --------------------------------
