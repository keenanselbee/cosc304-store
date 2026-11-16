"""Lab 8 TODO: show information for the currently logged-in customer."""

from flask import Blueprint, session
from db import get_connection
from html_utils import escape_html, html_page
from routes.auth import require_login

bp = Blueprint("customer", __name__)


@bp.get("/customer")
def customer_information():
    redirect_response = require_login()
    if redirect_response is not None:
        return redirect_response

    username = session["authenticatedUser"]
    # TODO: Use a parameterized SQL query to find customer.userid = username.
    #       Do not use a customer ID submitted in the URL.
    # TODO: Display customer name/contact/address, but NEVER the password.
    # TODO: Handle a missing customer record; close database resources.
    return html_page("Customer Information", """
        <h1>Customer Information</h1>
        <p>TODO: display information for the current customer.</p>
        <p><a href="/">Main Page</a></p>
    """)
