"""Lab 8 TODO: check customer credentials against SQL Server."""

from flask import Blueprint, current_app, redirect, request, session, url_for
from db import get_connection

bp = Blueprint("validate_login", __name__)


@bp.post("/validateLogin")
def validate_login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    valid_login = False  # Nobody is authenticated until the TODO is completed.

    if username and password:
        # TODO: Open a database connection using get_connection().
        # TODO: Use a parameterized SQL query (with ? placeholders) to
        #       check customer.userid and customer.password.
        # TODO: Set valid_login = True only if a matching row exists.
        #       Close the cursor/connection. Handle database errors.
        pass

    if valid_login:
        session["authenticatedUser"] = username
        session.pop("loginMessage", None)
        return redirect(url_for("index"))

    session.pop("authenticatedUser", None)
    session["loginMessage"] = "Invalid user ID or password."
    return redirect(url_for("login.login_page"))
