from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.test import TestCase
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from restaurant.models import Booking, Menu
from restaurant.serializers import MenuSerializer

User = get_user_model()
PASSWORD = "Citrus!River2026#"
MENU = "/restaurant/api/menu/"
BOOKINGS = "/restaurant/api/booking/tables/"
AUTH = "/restaurant/auth/"


class HomeTests(TestCase):
    def test_home_and_restaurant_serve_html(self):
        for url in ["/", "/restaurant/"]:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Good food.")
            self.assertContains(response, "/static/restaurant/style.css")

    def test_stylesheet_exists(self):
        self.assertIsNotNone(finders.find("restaurant/style.css"))


class AuthenticationTests(APITestCase):
    def test_registration_hashes_password_and_cannot_grant_staff(self):
        response = self.client.post(AUTH + "users/", {
            "username": "newguest", "email": "guest@example.com",
            "password": PASSWORD, "is_staff": True, "is_superuser": True,
        })
        self.assertEqual(response.status_code, 201)
        self.assertNotIn("password", response.data)
        user = User.objects.get(username="newguest")
        self.assertTrue(user.check_password(PASSWORD))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_duplicate_username_is_rejected(self):
        payload = {"username": "guest", "email": "guest@example.com", "password": PASSWORD}
        self.assertEqual(self.client.post(AUTH + "users/", payload).status_code, 201)
        self.assertEqual(self.client.post(AUTH + "users/", payload).status_code, 400)

    def test_weak_password_is_rejected(self):
        response = self.client.post(AUTH + "users/", {
            "username": "guest", "email": "guest@example.com", "password": "123",
        })
        self.assertEqual(response.status_code, 400)

    def test_real_token_login_and_logout(self):
        user = User.objects.create_user(username="guest", password=PASSWORD)
        response = self.client.post(AUTH + "token/login/", {"username": "guest", "password": PASSWORD})
        self.assertEqual(response.status_code, 200)
        key = response.data["token"]
        self.assertEqual(Token.objects.get(key=key).user, user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + key)
        self.assertEqual(self.client.get(BOOKINGS).status_code, 200)
        self.assertEqual(self.client.post(AUTH + "token/logout/").status_code, 204)
        self.assertEqual(self.client.get(BOOKINGS).status_code, 401)

    def test_invalid_credentials(self):
        self.assertEqual(self.client.post(AUTH + "token/login/", {
            "username": "absent", "password": "wrong",
        }).status_code, 400)


class DjoserAuthenticationTests(APITestCase):
    def test_registration_token_login_profile_and_logout(self):
        response = self.client.post("/auth/users/", {
            "username": "djoserguest", "email": "djoser@example.com", "password": PASSWORD,
        })
        self.assertEqual(response.status_code, 201)
        self.assertNotIn("password", response.data)
        self.assertTrue(User.objects.get(username="djoserguest").check_password(PASSWORD))
        login = self.client.post("/auth/token/login/", {"username": "djoserguest", "password": PASSWORD})
        self.assertEqual(login.status_code, 200)
        token = login.data["auth_token"]
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token)
        profile = self.client.get("/auth/users/me/")
        self.assertEqual(profile.status_code, 200)
        self.assertEqual(profile.data["username"], "djoserguest")
        self.assertEqual(self.client.get(BOOKINGS).status_code, 200)
        self.assertEqual(self.client.post("/auth/token/logout/").status_code, 204)
        self.assertFalse(Token.objects.filter(key=token).exists())
        self.assertEqual(self.client.get(BOOKINGS).status_code, 401)

    def test_registration_cannot_grant_staff_or_superuser(self):
        response = self.client.post("/auth/users/", {
            "username": "safeguest", "email": "safe@example.com", "password": PASSWORD,
            "is_staff": True, "is_superuser": True,
        })
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(username="safeguest")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_weak_password_and_duplicate_username_are_rejected(self):
        payload = {"username": "uniqueguest", "email": "unique@example.com", "password": PASSWORD}
        self.assertEqual(self.client.post("/auth/users/", {**payload, "password": "123"}).status_code, 400)
        self.assertEqual(self.client.post("/auth/users/", payload).status_code, 201)
        self.assertEqual(self.client.post("/auth/users/", payload).status_code, 400)

    def test_api_token_auth_route_returns_a_working_token(self):
        user = User.objects.create_user(username="tokenuser", password=PASSWORD)
        response = self.client.post("/restaurant/api-token-auth/", {"username": "tokenuser", "password": PASSWORD})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.get(key=response.data["token"]).user, user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + response.data["token"])
        self.assertEqual(self.client.get(BOOKINGS).status_code, 200)


class BrowsableAPITests(APITestCase):
    def test_menu_and_authenticated_api_root_render_html(self):
        menu = self.client.get(MENU, HTTP_ACCEPT="text/html")
        self.assertEqual(menu.status_code, 200)
        self.assertIn("text/html", menu["Content-Type"])
        self.assertContains(menu, "<html")
        user = User.objects.create_user(username="browserguest", password=PASSWORD)
        self.client.force_authenticate(user)
        root = self.client.get("/restaurant/api/", HTTP_ACCEPT="text/html")
        self.assertEqual(root.status_code, 200)
        self.assertContains(root, "<html")


class MenuAPITests(APITestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="staff", password=PASSWORD, is_staff=True)
        self.guest = User.objects.create_user(username="guest", password=PASSWORD)
        self.item = Menu.objects.create(title="Greek Salad", price="12.50", inventory=10)

    def test_public_list_and_serializer(self):
        response = self.client.get(MENU)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"], MenuSerializer([self.item], many=True).data)

    def test_public_detail(self):
        self.assertEqual(self.client.get(f"{MENU}{self.item.pk}/").data["title"], "Greek Salad")

    def test_anonymous_and_customer_cannot_write(self):
        payload = {"title": "Soup", "price": "9.50", "inventory": 5}
        self.assertEqual(self.client.post(MENU, payload).status_code, 401)
        self.client.force_authenticate(self.guest)
        self.assertEqual(self.client.post(MENU, payload).status_code, 403)
        self.assertEqual(self.client.patch(f"{MENU}{self.item.pk}/", {"price": "1.00"}).status_code, 403)
        self.assertEqual(self.client.delete(f"{MENU}{self.item.pk}/").status_code, 403)

    def test_staff_crud(self):
        self.client.force_authenticate(self.staff)
        response = self.client.post(MENU, {"title": "Soup", "price": "9.50", "inventory": 5})
        self.assertEqual(response.status_code, 201)
        url = f"{MENU}{response.data['id']}/"
        self.assertEqual(self.client.put(url, {"title": "Soup", "price": "10.00", "inventory": 4}).status_code, 200)
        self.assertEqual(self.client.patch(url, {"inventory": 3}).status_code, 200)
        self.assertEqual(self.client.delete(url).status_code, 204)
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_invalid_price_inventory_and_duplicate_title(self):
        self.client.force_authenticate(self.staff)
        for payload in [
            {"title": "Soup", "price": "0.00", "inventory": 1},
            {"title": "Soup", "price": "5.00", "inventory": -1},
            {"title": "Greek Salad", "price": "5.00", "inventory": 1},
        ]:
            self.assertEqual(self.client.post(MENU, payload).status_code, 400)

    def test_search_ordering_and_pagination(self):
        Menu.objects.bulk_create([Menu(title=f"Dish {i:02d}", price=i + 1, inventory=5) for i in range(12)])
        response = self.client.get(MENU, {"search": "Dish", "ordering": "-price"})
        self.assertEqual(response.data["count"], 12)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertEqual(response.data["results"][0]["title"], "Dish 11")
        self.assertIsNotNone(response.data["next"])
        self.assertEqual(len(self.client.get(MENU, {"search": "Dish", "page": 2}).data["results"]), 2)


class BookingAPITests(APITestCase):
    def setUp(self):
        self.guest = User.objects.create_user(username="guest", password=PASSWORD)
        self.other = User.objects.create_user(username="other", password=PASSWORD)
        self.staff = User.objects.create_user(username="staff", password=PASSWORD, is_staff=True)
        self.date = timezone.now() + timedelta(days=7)
        self.foreign = Booking.objects.create(user=self.other, name="Other", no_of_guests=2, booking_date=self.date)
        self.payload = {"name": "Guest", "no_of_guests": 3, "booking_date": self.date.isoformat()}

    def test_authentication_required(self):
        self.assertEqual(self.client.get(BOOKINGS).status_code, 401)
        self.assertEqual(self.client.post(BOOKINGS, self.payload).status_code, 401)

    def test_owner_crud_and_user_field_is_read_only(self):
        self.client.force_authenticate(self.guest)
        response = self.client.post(BOOKINGS, {**self.payload, "user": self.other.pk})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["user"], self.guest.pk)
        url = f"{BOOKINGS}{response.data['id']}/"
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(self.client.put(url, {**self.payload, "no_of_guests": 4}).status_code, 200)
        self.assertEqual(self.client.patch(url, {"no_of_guests": 5}).status_code, 200)
        self.assertEqual(self.client.delete(url).status_code, 204)

    def test_customers_only_see_their_own_bookings(self):
        self.client.force_authenticate(self.guest)
        self.assertEqual(self.client.get(BOOKINGS).data["count"], 0)
        url = f"{BOOKINGS}{self.foreign.pk}/"
        for response in [self.client.get(url), self.client.patch(url, {"name": "Changed"}), self.client.delete(url)]:
            self.assertEqual(response.status_code, 404)

    def test_staff_can_list_update_delete_all_bookings(self):
        self.client.force_authenticate(self.staff)
        self.assertEqual(self.client.get(BOOKINGS).data["count"], 1)
        url = f"{BOOKINGS}{self.foreign.pk}/"
        self.assertEqual(self.client.patch(url, {"no_of_guests": 4}).status_code, 200)
        self.assertEqual(self.client.delete(url).status_code, 204)

    def test_past_date_and_invalid_guest_counts(self):
        self.client.force_authenticate(self.guest)
        for overrides in [
            {"booking_date": (timezone.now() - timedelta(days=1)).isoformat()},
            {"no_of_guests": 0}, {"no_of_guests": 21}, {"name": ""},
        ]:
            self.assertEqual(self.client.post(BOOKINGS, {**self.payload, **overrides}).status_code, 400)

    def test_duplicate_time_is_rejected_but_other_customers_can_book(self):
        self.client.force_authenticate(self.guest)
        self.assertEqual(self.client.post(BOOKINGS, self.payload).status_code, 201)
        self.assertEqual(self.client.post(BOOKINGS, self.payload).status_code, 400)

    def test_update_cannot_duplicate_another_own_booking(self):
        self.client.force_authenticate(self.guest)
        first = self.client.post(BOOKINGS, self.payload)
        second = self.client.post(BOOKINGS, {**self.payload, "booking_date": (self.date + timedelta(hours=1)).isoformat()})
        self.assertEqual(first.status_code, 201)
        self.assertEqual(self.client.patch(f"{BOOKINGS}{second.data['id']}/", {"booking_date": self.date.isoformat()}).status_code, 400)
