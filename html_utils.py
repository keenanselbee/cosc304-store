"""Small HTML helpers. Full template engines are not required for this lab."""

from decimal import Decimal
from html import escape
from flask import render_template, request, session, url_for


def escape_html(value):
    return escape("" if value is None else str(value), quote=True)


def format_currency(value):
    amount = Decimal(str(value))
    number = f"{amount:.0f}" if amount == amount.to_integral_value() else f"{amount:.2f}"
    label = "elf ear" if amount == 1 else "elf ears"
    return (f'<span class="price" aria-label="{number} {label}">{number}'
            '<img class="ear-icon" src="/static/images/elf-ear-bloody.png" alt=""></span>')


def html_page(title, body, *, shop=False):
    return render_template("page.html", title=title, body=body, shop=shop,
                           endpoint=request.endpoint or "", user_name=session.get("authenticatedUser"))


def image_source(image_url):
    if image_url and not image_url.startswith(("http://", "https://", "/")):
        return url_for("static", filename=image_url)
    return image_url
