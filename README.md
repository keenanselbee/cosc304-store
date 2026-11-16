# COSC 304 - Online Store

Database-enabled store using Python, Flask, and SQL Server.\
Team Members: Mathijs Deelen, Keenan Selbee\
Python Version: 3.12\
Required Software: Docker Desktop

**Set up from project root:**

Optional: create a local virtual environment for editor tooling using Python 3.12. Docker runs the application separately.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

**Start application from project root:**

With Docker Desktop running:

```powershell
docker compose up -d --build
```

**Load the Gruk theme:** After SQL Server is ready, run once:

```powershell
docker exec -w /app cosc304-python python theme.py
```

This sets up eight shop products and themes the remaining sample products as past stock.\
On the first run, the five supplied orders receive elf-ear prices and matching totals.\
Product IDs, order quantities and inventory quantities stay the same.

**Demo login:** Username: `gruk` Password: `axe` Customer ID: `1`

Theme setup gives sample customer 1 Gruk's name and fictional shop contact details,
preserves its existing orders, and restores the account after a database reset.

**Application routes:**

Base URL: `http://localhost`. GET routes can be opened in the browser; POST routes are submitted through the application's forms.

| Method | Route | Purpose |
| --- | --- | --- |
| GET | `/` | Show the shop with product search and category filters |
| GET | `/listprod` | List products; accepts optional `productName` and `category` query parameters |
| GET | `/product?id=1` | Show one product's details and both image types |
| GET | `/displayImage?id=1` | Return the product's database image as PNG or JPEG |
| GET | `/addcart` | Add an item to the session cart using `id`, `name` and `price` query parameters |
| GET | `/showcart` | Show cart items, quantities and totals |
| GET | `/checkout` | Show the customer-ID checkout form |
| POST | `/order` | Validate checkout, confirm changed prices when needed and save the order |
| GET | `/listorder` | Show saved orders and their items |
| GET | `/login` | Show the login form |
| POST | `/validateLogin` | Check credentials and set the authenticated session identity |
| GET | `/logout` | Log out while preserving the cart |
| GET | `/customer` | Show the logged-in customer's information; requires login |
| GET | `/admin` | Show daily sales totals; requires login |
| GET | `/ship?orderId=1` | Process a shipment from warehouse 1 and update inventory on success |
| GET | `/loaddata` | Check the database connection and show the reset form |
| POST | `/loaddata` | Delete current store data and restore the themed sample data |

**Tests:** With both Docker services running and the lab database loaded, run:

```powershell
docker exec -w /app cosc304-python python -m unittest discover -s tests -v
```

`tests/test_lab7.py` checks search, cart and orders.\
`tests/test_lab8.py` checks images, login, customer information, sales and shipments.\
Shared helpers are in `tests/support.py`.
`tests/test_theme.py` checks category search, past-stock restrictions and repeatable theme setup.\
Run the tests after applying the theme. The tests use the local SQL Server database and clean up their records.

**Useful commands:**

```powershell
docker compose ps                # Check running services
docker compose logs -f app       # View application logs
docker compose stop              # Stop services
docker compose up -d             # Restart services
docker compose down              # Remove containers and preserve database
```

Do not use `docker compose down -v` unless you intend to delete the stored database.

**Project structure:**

```text
root/
|-- routes/               Store routes and database operations
|   |-- listprod.py        Product search and category filters
|   |-- product.py         Product details
|   |-- display_image.py   Database image response
|   |-- listorder.py       Order listing
|   |-- order.py           Save purchases
|   |-- addcart.py         Cart handling
|   |-- showcart.py        Cart display
|   |-- checkout.py        Customer ID form
|   |-- login.py           Login form
|   |-- validate_login.py  Check credentials
|   |-- logout.py          End login session
|   |-- auth.py            Login requirement helper
|   |-- customer.py        Logged-in customer details
|   |-- admin.py           Daily sales report
|   |-- ship.py            Shipment transaction
|   |-- loaddata.py        Database check and reset
|   `-- __init__.py        Routes package
|-- views/                Shared page, shop and product templates
|-- static/
|   |-- css/               Shared shop styling
|   |-- js/                Gruk dialogue animation
|   |-- images/            Theme artwork and product image pairs
|   `-- img/               Original starter product images
|-- images/mockups/       Selected design references
|-- tests/                Lab 7, Lab 8 and theme integration tests
|-- ddl/                  Database setup and sample data
|-- examples/             Instructor reference examples
|-- docs/                 Design decisions, shop content, asset prompts and provenance
|-- app.py                Flask application
|-- db.py                 Database connection helper
|-- html_utils.py         HTML and currency formatting
|-- theme.py              Repeatable catalogue and demo-account setup
|-- requirements.txt      Python dependencies
|-- Dockerfile            Application environment
|-- docker-compose.yml    Application and database services
|-- .gitignore
`-- README.md
```

**Sources:**

Based on the [COSC 304 Python starter](https://github.com/rlawrenc/cosc_304/tree/main/labs/lab7/python).
