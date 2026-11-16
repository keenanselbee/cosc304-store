"""Shared login guard for the Lab 8 customer and administrator pages."""

from flask import redirect, session, url_for


def require_login():
    """Return a login redirect if needed; otherwise return None."""
    if session.get("authenticatedUser") is None:
        session["loginMessage"] = "Please log in to access that page."
        return redirect(url_for("login.login_page"))
    return None
