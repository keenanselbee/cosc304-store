"""Log out without deleting the Lab 7 shopping cart."""

from flask import Blueprint, redirect, session, url_for

bp = Blueprint("logout", __name__)


@bp.get("/logout")
def log_out():
    session.pop("authenticatedUser", None)
    session.pop("loginMessage", None)
    return redirect(url_for("index"))
