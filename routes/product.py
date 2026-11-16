"""Lab 8 TODO: product details with URL and database images."""

from flask import Blueprint, request
from db import get_connection
from html_utils import escape_html, format_currency, html_page

bp = Blueprint("product", __name__)


@bp.get("/product")
def product_details():
    product_id_text = request.args.get("id", "")

    # TODO: Validate that id is a positive integer product ID.
    # TODO: Query product by ID using a parameterized SQL query.
    #       Retrieve productId, productName, productPrice, productDesc,
    #       productImageURL, and whether productImage is present.
    # TODO: Handle an invalid ID or a product not found.
    # TODO: Display the name, price and description, escaping HTML text.
    # TODO: For productImageURL (e.g. img/1.jpg), build an HTML <img> tag.
    #       The new local files are served from /static/img/1.jpg, etc.
    # TODO: For a database image, set <img src="/displayImage?id=...">.
    # TODO: Add a link to Lab 7's /addcart route with id, name, price.
    #       Flask's url_for() safely URL-encodes query parameters.
    return html_page("Product Details", """
        <h1>Product Details</h1>
        <p>TODO: retrieve and display the selected product.</p>
        <p><a href="/listprod">Continue Shopping</a> |
           <a href="/">Main Page</a></p>
    """)
