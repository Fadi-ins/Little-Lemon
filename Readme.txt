LITTLE LEMON WEB APPLICATION
==========================
Django REST Framework back-end capstone: static HTML homepage, MySQL,
menu CRUD, authenticated table booking CRUD, registration, and token login.

REVIEWER QUICK START (WINDOWS POWERSHELL)
1. Install Python 3.12+ and MySQL 8.4. Open this folder in VS Code.
2. Create a virtual environment and install packages:
     python -m venv .venv
     .\.venv\Scripts\python.exe -m pip install -r requirements.txt
3. Copy the example environment file:
     Copy-Item .env.example .env
   Edit .env: set DJANGO_SECRET_KEY to a long random string and configure
   your MySQL username, password, host, port, and database name.
   Generate a secret with:
     .\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(50))"
4. In the MySQL client, as a database administrator, run:
     CREATE DATABASE littlelemon CHARACTER SET utf8mb4;
     CREATE USER 'littlelemon'@'localhost' IDENTIFIED BY 'your-local-password';
     GRANT ALL PRIVILEGES ON littlelemon.* TO 'littlelemon'@'localhost';
     GRANT ALL PRIVILEGES ON test_littlelemon.* TO 'littlelemon'@'localhost';
   Put that password in .env. The test database grant is for local tests.
   If the user or databases already exist, reuse them instead of recreating them.
5. Prepare and run the app:
     .\.venv\Scripts\python.exe manage.py migrate
     .\.venv\Scripts\python.exe manage.py seed_menu
     .\.venv\Scripts\python.exe manage.py createsuperuser
     .\.venv\Scripts\python.exe manage.py runserver
6. Open http://127.0.0.1:8000/ in a browser.
7. Run tests in a second terminal:
     .\.venv\Scripts\python.exe manage.py test restaurant.tests -v 2

macOS/Linux: use python3 -m venv .venv, then .venv/bin/python in place of
.\.venv\Scripts\python.exe. mysqlclient requires your platform's MySQL
development libraries and pkg-config if a binary wheel is unavailable.

OPTIONAL DOCKER DATABASE
With Docker Compose installed, add MYSQL_ROOT_PASSWORD to .env and run:
  docker compose up -d --wait
Use MYSQL_HOST=127.0.0.1 in .env. Apply the test database grant using the
root account inside the container before running tests. The Django app
runs locally, not inside the container. Stop the database with:
  docker compose down

API PATHS TO TEST
Base URL: http://127.0.0.1:8000
All API paths end with a slash. Send JSON with Content-Type: application/json.

GET     /                                      Static HTML restaurant homepage
GET     /restaurant/                           Same homepage
GET     /restaurant/api/                       Browsable API root
POST    /restaurant/auth/users/                Register a customer
POST    /restaurant/auth/token/login/          Obtain an API token
POST    /restaurant/auth/token/logout/         Revoke the current API token
GET     /restaurant/api/menu/                  List menu (public)
POST    /restaurant/api/menu/                  Create menu item (staff)
GET     /restaurant/api/menu/<id>/             Retrieve menu item (public)
PUT     /restaurant/api/menu/<id>/             Replace menu item (staff)
PATCH   /restaurant/api/menu/<id>/             Partially update menu item (staff)
DELETE  /restaurant/api/menu/<id>/             Delete menu item (staff)
GET     /restaurant/api/booking/tables/         List own bookings (authenticated)
POST    /restaurant/api/booking/tables/         Create own booking (authenticated)
GET     /restaurant/api/booking/tables/<id>/    Retrieve own booking
PUT     /restaurant/api/booking/tables/<id>/    Replace own booking
PATCH   /restaurant/api/booking/tables/<id>/    Partially update own booking
DELETE  /restaurant/api/booking/tables/<id>/    Delete own booking
GET     /admin/                                Django admin login
GET     /api-auth/login/                       Browsable API session login

STAFF AND OWNERSHIP
The superuser created above is staff and can create/edit/delete menu items
and view/update/delete all bookings. Registered customers cannot grant
themselves staff status. Customers can only access their own bookings;
requests for another customer's booking return 404. The server assigns
the booking owner, ignoring any user ID in a create/update request.

INSOMNIA WALKTHROUGH
Import insomnia/Little-Lemon.json using Insomnia's Import > File option.
This is a native Insomnia v4 export. Set the collection environment values:
base_url, username, email, password, staff_username, and staff_password.
Use a strong password for the new test account. No credentials are bundled.
1. Send 'Register customer'. Expected: 201; password is not returned.
2. Send 'Customer login'. Expected: 200 with {"token":"..."}.
   Copy the returned token to the customer_token environment value.
3. Send 'List menu'. Expected: 200, with count/next/previous/results.
   Search/order example: /restaurant/api/menu/?search=salad&ordering=price
   Pagination example: /restaurant/api/menu/?page=1
4. Send 'Staff login' using your createsuperuser credentials. Copy its token
   into staff_token. Send 'Create menu item' and copy its id into menu_id.
   Test GET, PUT, PATCH, and DELETE using the menu detail requests.
5. Set booking_date to a future ISO 8601 timestamp with timezone, for example
   2030-12-01T19:00:00+03:00. Send 'Create booking'. Expected: 201.
   Copy its id into booking_id, then retrieve, replace, and patch it.
6. Repeat the create request with the same user and time: expected 400.
   Zero guests, more than 20 guests, and past dates also return 400.
   Each booking is one reservation; this project does not model physical
   table allocation, restaurant opening hours, or total seating capacity.
7. Register and log in as a second customer (change environment values).
   Their bookings list excludes the first customer's records. Direct access
   to the first customer's booking returns 404. Staff can see all bookings.
8. Delete your booking: expected 204. Log out: expected 204. Requests with
   the revoked token then return 401. Use token auth when testing logout;
   browser session logout is available separately through /api-auth/logout/.

EXAMPLE JSON BODIES
Registration:
  {"username":"reviewer","email":"reviewer@example.com","password":"your-strong-local-password"}
Login (works for customers and staff):
  {"username":"reviewer","password":"your-strong-local-password"}
Menu:
  {"title":"Pasta","price":"14.00","inventory":20}
Booking:
  {"name":"Review Guest","no_of_guests":2,"booking_date":"2030-12-01T19:00:00+03:00"}

AUTHENTICATION HEADER
  Authorization: Token <the-token-returned-by-login>
Menu reads and registration/login are public. Protected endpoints require
a valid token, or a session established through /api-auth/login/.
Wrong login details return 400. Unauthenticated protected requests return
401; authenticated non-staff menu writes return 403; missing/foreign booking
IDs return 404. Invalid JSON fields and duplicate bookings return 400.
Create returns 201, reads/updates 200, deletes/logout 204 (empty body).

PROJECT NOTES
MySQL is the configured database; there is no implicit SQLite fallback.
Migrations are committed. seed_menu is safe to rerun and leaves existing
records unchanged. Tests use Django's separate test database and do not
need sample menu data, a running web server, or fixed user credentials.
Credentials, tokens, local database files, and virtual environments are
excluded from Git. Development DEBUG is opt-in via .env. Use HTTPS and
production hosting settings before exposing token authentication online.

References:
https://docs.djangoproject.com/en/5.2/ref/databases/
https://www.django-rest-framework.org/api-guide/authentication/
https://www.django-rest-framework.org/api-guide/testing/
