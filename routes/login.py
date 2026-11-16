"""Login form (provided for Lab 8)."""

from flask import Blueprint, session, url_for
from html_utils import escape_html, html_page

bp = Blueprint("login", __name__)


@bp.get("/login")
def login_page():
    message = session.pop("loginMessage", None)
    notice = f"<p>{escape_html(message)}</p>" if message else ""
    return html_page("Log In", f"""
        <h1>Log In</h1>
        {notice}
        <form method="post" action="{url_for('validate_login.validate_login')}">
          <p><label>User ID:
             <input name="username" type="text" maxlength="20" required>
          </label></p>
          <p><label>Password:
             <input name="password" type="password" maxlength="30" required>
          </label></p>
          <p><button type="submit">Log In</button></p>
        </form>
        <p><a href="/">Main Page</a></p>
    """)
