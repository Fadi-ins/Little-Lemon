# Little Lemon Web Application

A Django REST Framework restaurant application backed by MySQL. Includes a
restaurant homepage, menu API, table booking API, customer registration,
token authentication, and automated tests.

Start with [Readme.txt](Readme.txt) for setup commands, API paths, permissions,
JSON examples, and the complete reviewer walkthrough.

Import [the Insomnia collection](insomnia/Little-Lemon.json) to exercise the
API. Credentials and tokens are configured locally and are not included.

## Main endpoints

| Path | Purpose |
| --- | --- |
| `/` | Restaurant HTML homepage |
| `/restaurant/api/menu/` | Public menu reads, staff writes |
| `/restaurant/api/booking/tables/` | Authenticated booking CRUD |
| `/restaurant/auth/users/` | Customer registration |
| `/restaurant/auth/token/login/` | Token login |
| `/restaurant/auth/token/logout/` | Token revocation |
| `/admin/` | Django administration |

Customers manage their own bookings. Staff can manage all bookings. Menu
search, ordering, and pagination are supported. Booking dates must be in
the future, party sizes must be 1–20, and duplicate reservations for the same
customer and timestamp are rejected.
