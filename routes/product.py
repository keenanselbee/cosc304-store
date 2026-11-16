"""Lab 8 product details with URL and database images."""

from flask import Blueprint, current_app, request, url_for
from db import get_connection
from html_utils import escape_html, format_currency, html_page

bp = Blueprint("product", __name__)


@bp.get("/product")
def product_details():
    product_id_text = request.args.get("id", "")

    # --------------------------------

    shopping_link = url_for("listprod.list_products")
    navigation = (f'<p><a href="{escape_html(shopping_link)}">Continue Shopping</a> | '
                  f'<a href="{escape_html(url_for("index"))}">Main Page</a></p>')

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
        query = """SELECT productId, productName, productPrice, productDesc, productImageURL, productImage
                   FROM product
                   WHERE productId = ?"""
        cursor.execute(query, [product_id])
        product = cursor.fetchone()

        if product is None:
            return html_page("Product Details", "<p>Product not found</p>" + navigation), 404

        product_id, name, price, description, image_url, image_data = product
        output = [f"<h1>{escape_html(name)}</h1>",
                  f"<p>Product ID: {product_id}</p>",
                  f"<p>Price: {format_currency(price)}</p>",
                  f"<p>{escape_html(description)}</p>"]

        if image_url:
            # starter image paths are relative to the static folder
            if not image_url.startswith(("http://", "https://", "/")):
                image_url = url_for("static", filename=image_url)
            output.append(
                f'<img src="{escape_html(image_url)}" alt="{escape_html(name)}" width="300">')

        if image_data is not None:
            image_link = url_for("display_image.display_image", id=product_id)
            output.append(
                f'<img src="{escape_html(image_link)}" alt="{escape_html(name)}" width="300">')

        cart_link = url_for("addcart.add_to_cart", id=product_id, name=name, price=price)
        output.append(f'<p><a href="{escape_html(cart_link)}">Add to Cart</a></p>')
        output.append(navigation)
        return html_page(name, "".join(output))
    except Exception:
        current_app.logger.exception("Unable to load product")
        return html_page("Product Details", "<p>Unable to load product</p>" + navigation), 500
    finally:
        if connection is not None:
            connection.close()

    # --------------------------------
