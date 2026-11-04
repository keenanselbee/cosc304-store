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

**Application pages:**

| Page | URL |
|---|---|
| Store | http://localhost/ |
| Database connection check | http://localhost/loaddata |
| Product list | http://localhost/listprod |
| Order list | http://localhost/listorder |
| Shopping cart | http://localhost/showcart |
| Checkout | http://localhost/checkout |

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
├── routes/               Store routes and database operations
│   ├── listprod.py        Product search
│   ├── listorder.py       Order listing
│   ├── order.py           Save purchases
│   ├── addcart.py         Cart handling
│   ├── showcart.py        Cart display
│   ├── checkout.py        Customer ID form
│   ├── loaddata.py        Database check and reset
│   └── __init__.py        Routes package
├── views/                Store landing page
├── ddl/                  Database setup and sample data
├── examples/             Instructor reference examples
├── docs/
│   ├── lab7-design-decisions.md
│   └── PROVENANCE.md
├── app.py                Flask application
├── db.py                 Database connection helper
├── html_utils.py         HTML and currency formatting
├── requirements.txt      Python dependencies
├── Dockerfile            Application environment
├── docker-compose.yml    Application and database services
├── .gitignore
└── README.md
```

**Sources:**

Based on the [COSC 304 Python starter](https://github.com/rlawrenc/cosc_304/tree/main/labs/lab7/python).
