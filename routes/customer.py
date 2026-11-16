"""Lab 8 TODO: show information for the currently logged-in customer."""

from flask import Blueprint, current_app, session
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
    # --------------------------------
    # get the logged in customer
    connection = None
    cursor = None
    navigation = '<p><a href="/">Main Page</a></p>'
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = """SELECT customerId, firstName, lastName, email, phonenum,
                    address, city, state, postalCode, country, userid
                    FROM customer
                    WHERE userid = ?"""
        cursor.execute(query, [username])
        customer = cursor.fetchone()

        if customer is None:
            return html_page("Customer Information",
                             "<p>Customer info not found</p>" + navigation), 404

        labels = ["Customer ID", "First name", "Last name", "Email", "Phone",
                  "Address", "City", "State or province", "Postal code", "Country", "User ID"]
        output = ['<h1>Customer Information</h1><table border="1">']
        for label, value in zip(labels, customer):
            output.append(f"<tr><th>{label}</th><td>{escape_html(value)}</td></tr>")
        output.append("</table>" + navigation)
        return html_page("Customer Information", "".join(output))
    except Exception:
        current_app.logger.exception("Unable to load customer info")
        return html_page("Customer Information",
                         "<p>Unable to load customer info</p>" + navigation), 500
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
    # --------------------------------
