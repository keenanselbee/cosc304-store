"""Lab 8 TODO: daily administrator sales report."""

from flask import Blueprint, current_app
from db import get_connection
from html_utils import escape_html, format_currency, html_page
from routes.auth import require_login

bp = Blueprint("admin", __name__)


@bp.get("/admin")
def admin_report():
    # --------------------------------
    # check login before loading sales
    redirect_response = require_login()
    if redirect_response is not None:
        return redirect_response

    connection = None
    cursor = None
    navigation = '<p><a href="/">Main Page</a></p>'
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = """SELECT CAST(orderDate AS date), SUM(totalAmount)
                   FROM ordersummary
                   GROUP BY CAST(orderDate AS date)
                   ORDER BY CAST(orderDate AS date)"""
        cursor.execute(query)

        rows = []
        # turn each result into a table
        for row in cursor:
            sales_date, total = row
            rows.append(f"<tr><td>{escape_html(sales_date)}</td>"
                        f"<td>{format_currency(total)}</td></tr>")

        output = "<h1>Daily Sales Report</h1>"
        if rows:
            output += ('<table border="1"><tr><th>Date</th><th>Total sales</th></tr>'
                       + "".join(rows) + "</table>")
        else:
            output += "<p>No sales found</p>"
        return html_page("Administrator Report", output + navigation)
    except Exception:
        current_app.logger.exception("Unable to load sales report")
        return html_page("Administrator Report",
                         "<p>Unable to load sales report</p>" + navigation), 500
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
    # --------------------------------
