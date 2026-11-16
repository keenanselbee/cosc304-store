"""COSC 304 Lab 7 and Lab 8 store and examples, served by Flask."""

import os

from flask import Flask, render_template, session

from routes import addcart, checkout, listorder, listprod, loaddata, order, showcart
from routes import admin, customer, display_image, login, logout, product, ship, validate_login
from examples import register_examples

app = Flask(__name__, template_folder="views")
# Local student-development setting; use a random secret stored outside code in production.
app.secret_key = os.getenv("FLASK_SECRET_KEY", "cosc304-local-lab-session-secret")


@app.get("/")
def index():
    return render_template("index.html", user_name=session.get("authenticatedUser"))


for module in (loaddata, listorder, listprod, addcart, showcart, checkout, order,
               login, validate_login, logout, product, display_image, admin, customer, ship):
    app.register_blueprint(module.bp)
register_examples(app)

if __name__ == "__main__":
    # Reloader picks up student edits; debugger deliberately disabled.
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=True)
