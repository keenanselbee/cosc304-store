# COSC 304 — Lab 8 Python/Flask starter add-on

> Original instructor starter reference. The installation steps and TODO descriptions below describe the supplied add-on before implementation, not the current store. For current setup and usage, see the [project README](../README.md).

This package adds the **Lab 8 Flask routes and product images** to your existing Lab 7 Python web store. It is **not a standalone project**.

## Install

1. Start with your **existing** `cosc304-python` Lab 7 project. Do not reset the SQL Server database.
2. If you customized your Lab 7 home page or Flask setup, **save copies of `views/index.html` and `app.py` first**. This ZIP contains updated versions of both files, which **replace the Lab 7 versions**. Transfer any custom store name or other changes you wish to keep.
3. Extract the *contents* of this ZIP **directly into the `cosc304-python/` project directory**. Merge the `routes/` and `views/` folders, add `static/img/`, and allow **`app.py` and `views/index.html` to be overwritten**. Keep the Lab 7 `db.py`, `html_utils.py`, other existing routes, Docker configuration, `requirements.txt`, and database scripts unchanged.
4. The new home page already links to shopping, order history, login/logout, customer information, the administrator report, and shipment tests for orders 1 and 3. Change `YOUR NAME Grocery` to your store name in `views/index.html`.
5. Edit your **existing** `routes/listprod.py` so each product name links to `/product?id=<productId>`; retain its current Add to Cart link. The starter does **not** replace `routes/listprod.py`. For example, obtain the URL with `url_for("product.product_details", id=product_id)` and escape it before placing it in the HTML.
6. Complete the TODOs in the new Lab 8 Python files. The lab instructions are at https://github.com/rlawrenc/cosc_304/blob/main/labs/lab8/develop/README.md.

Start the existing Docker application and visit **http://localhost/**. The Python application runs on port 80 through the Lab 7 Docker setup (not `/shop/` as in Java). The source directory is already mounted into the container, so no Docker or SQL Server rebuild is needed to add these Python files. Restart the Flask app if the new routes are not registered immediately.

## New files provided

| File | Purpose |
| --- | --- |
| `app.py` | **Replaces the Lab 7 Flask entry point** and registers the new routes; keeps all Lab 7 routes |
| `views/index.html` | **Replaces the Lab 7 home page** with Lab 8 links and a logged-in username |
| `routes/admin.py` | TODO: login-protected daily sales report |
| `routes/auth.py` | Reusable login requirement helper |
| `routes/customer.py` | TODO: information for the logged-in customer |
| `routes/display_image.py` | TODO: return binary product images as JPEG HTTP responses |
| `routes/login.py` | Login form |
| `routes/logout.py` | Logout while preserving the shopping cart |
| `routes/product.py` | TODO: product details, URL and database images, cart link |
| `routes/ship.py` | TODO: transactionally ship all items from warehouse 1 |
| `routes/validate_login.py` | TODO: parameterized customer username/password validation |
| `static/img/1.jpg`, `1_a.jpg`, `2.jpg`, `3.jpg`, `4.jpg`, `5.jpg` | Product photos from the Java Lab 8 starter, served by Flask under `/static/img/` |

**Starter behavior:** The new home page, login form, logout route, and existing Lab 7 features are functional. Login intentionally fails until `routes/validate_login.py` is completed. Product, admin, customer, image-streaming, and shipment features remain incomplete until the TODOs are implemented. The sample database already contains the image URL and binary-image columns; do not reload it just for Lab 8.

**Python-specific notes:** Use parameterized SQL with pyodbc `?` placeholders (Python does not have JDBC's `PreparedStatement` class). The Java lab URL `product.jsp?id=1` corresponds to `/product?id=1` in Python; `ship.jsp?orderId=1` corresponds to `/ship?orderId=1`. Flask sessions preserve the Lab 7 shopping cart when you set or remove `session["authenticatedUser"]`.
