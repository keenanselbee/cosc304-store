"""Lab 8 TODO: daily administrator sales report."""

from flask import Blueprint
from db import get_connection
from html_utils import escape_html, format_currency, html_page
from routes.auth import require_login

bp = Blueprint("admin", __name__)


@bp.get("/admin")
def admin_report():
    # TODO: Call require_login() and return its redirect when needed.
    # TODO: Query total sales for each day from ordersummary. Use
    #       CAST(orderDate AS date), SUM(totalAmount), GROUP BY and ORDER BY.
    # TODO: Display the daily sales in an HTML table; close the connection.
    return html_page("Administrator Report", """
        <h1>Administrator Report</h1>
        <p>TODO: display daily total sales, after checking login.</p>
        <p><a href="/">Main Page</a></p>
    """)
