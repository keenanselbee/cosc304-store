"""Lab 8 TODO: serve productImage (VARBINARY) as an HTTP JPEG response."""

from flask import Blueprint, Response, current_app, request
from db import get_connection

bp = Blueprint("display_image", __name__)


@bp.get("/displayImage")
def display_image():
    raw_id = request.args.get("id", "")
    try:
        product_id = int(raw_id)
        if product_id <= 0 or product_id > 2147483647:
            raise ValueError()
    except ValueError:
        return "Invalid product ID", 400

    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        # The ? placeholder is a bound SQL parameter, not string substitution.
        cursor.execute("SELECT productImage FROM product WHERE productId = ?", product_id)
        row = cursor.fetchone()
        if row is None:
            return "Product not found", 404
        if row[0] is None:
            return "No database image for this product", 404

        # TODO: Convert the binary column value to bytes if necessary.
        # TODO: Return an HTTP response containing those bytes with the
        #       MIME type image/jpeg. Do NOT put image bytes in html_page().
        #       Hint: Flask's Response(data, mimetype="image/jpeg").
        return "Image streaming not implemented yet", 501
    except Exception:
        current_app.logger.exception("Unable to load database image")
        return "Unable to retrieve product image", 500
    finally:
        if connection is not None:
            connection.close()
