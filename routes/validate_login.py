"""Lab 8 TODO: check customer credentials against SQL Server."""

from flask import Blueprint, current_app, redirect, request, session, url_for
from db import get_connection

bp = Blueprint("validate_login", __name__)


@bp.post("/validateLogin")
def validate_login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    valid_login = False  # assume login fails

    if username and password:
        # --------------------------------
        # check the login
        connection = None
        cursor = None
        try:
            connection = get_connection()
            cursor = connection.cursor()
            query = """SELECT customerId
                        FROM customer
                        WHERE userid = ? AND password = ?"""
            cursor.execute(query, [username, password])
            valid_login = cursor.fetchone() is not None
        except Exception:
            current_app.logger.exception("Unable to check login")
        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()
        # --------------------------------

    if valid_login:
        session["authenticatedUser"] = username
        session.pop("loginMessage", None)
        return redirect(url_for("index"))

    session.pop("authenticatedUser", None)
    session["loginMessage"] = "Invalid username or password."
    return redirect(url_for("login.login_page"))
