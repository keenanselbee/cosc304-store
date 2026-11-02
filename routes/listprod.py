"""Question 2 (10 marks): display/search products and provide cart links."""

from flask import Blueprint, request, current_app
from flask import url_for
from db import get_connection
from html_utils import escape_html, format_currency, html_page

bp = Blueprint("listprod", __name__)


@bp.get("/listprod")
def list_products():
    name = request.args.get("productName", "")
    form = ("<h1>Search for the products you want to buy:</h1>"
            '<form method="get" action="/listprod">'
            f'<input type="text" name="productName" size="50" value="{escape_html(name)}">'
            '<input type="submit" value="Submit"> '
            '<input type="reset" value="Reset"> '
            '(Leave blank for all products)</form>')

    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()

        sql = "SELECT productId, productName, productPrice FROM product"

        if name.strip():
            cursor.execute(sql + " WHERE productName LIKE ?", f"%{name}%")
        else:
            cursor.execute(sql)

        products = cursor.fetchall()
        output = []

        if not products:
            output.append("<p>No matches</p>")
        else:
            output.append(
                '<table border="1">'
                "<tr><th>ID</th><th>Name</th><th>Price</th><th>Cart</th></tr>")

            for product_id, product_name, price in products:
                link = url_for(
                    "addcart.add_to_cart",
                    id=product_id,
                    name=product_name,
                    price=price)

                output.append(
                    f"<tr><td>{product_id}</td>"
                    f"<td>{escape_html(product_name)}</td>"
                    f"<td>{format_currency(price)}</td>"
                    f'<td><a href="{escape_html(link)}">Add to cart</a></td></tr>')

            output.append("</table>")

        return html_page("YOUR NAME Grocery", form + "".join(output))
    except Exception:
        current_app.logger.exception("Unable to list products")
        return html_page("Product Search Error", form +
                         "<p>Unable to search products.</p>"), 500
    finally:
        if connection is not None:
            connection.close()
