# Verification

Verified on November 12, 2026 with Python 3.14.3, Django 5.2.19,
Django REST Framework 3.16.1, Djoser 2.3.4, mysqlclient 2.3.1, and MySQL Community
Server 8.4.13. Dependencies are pinned in `requirements.txt`.

| Check | Result |
| --- | --- |
| Apply committed database migrations | Passed on MySQL |
| Seed sample menu | Passed |
| Django system check | No issues |
| Unit and API tests | 29 passed |
| Dependency compatibility (`pip check`) | No broken requirements |
| Migration consistency | No changes detected |

Run the same checks after configuring `.env` and a local MySQL user:

```sh
python manage.py migrate
python manage.py seed_menu
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test restaurant.tests -v 2
```

The test runner creates and removes `test_littlelemon` (or `test_` plus
your configured database name). Grant the local test user permission on
that database as described in `Readme.txt`.

Coverage includes model representation, positive menu prices, guest limits,
homepage/template rendering, static stylesheet discovery, registration,
password validation and hashing, token login and revocation, staff-only menu
writes, menu CRUD/search/order/pagination, booking CRUD, owner isolation,
staff access, server-assigned owners, duplicate bookings, and past dates.
Additional tests exercise Djoser registration, login, current-user profile,
token revocation, registration privilege protection, weak passwords,
duplicate usernames, the `api-token-auth` route, and browsable HTML API
responses. View tests are in `restaurant/tests/test_views.py`; model tests
are in `restaurant/tests/test_models.py`.

The project-level `templates` directory contains the homepage template.
`littlelemon/settings.py` includes that directory in `TEMPLATES[0]['DIRS']`.
`djoser` is included in `INSTALLED_APPS`, and project URL configuration
mounts both `djoser.urls` and `djoser.urls.authtoken` under `/auth/`.

The supplied Insomnia collection provides 24 manual HTTP requests for review;
the automated API tests run through DRF's test client. Import and execution
inside the Insomnia desktop application are separate manual checks.
