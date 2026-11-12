from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from restaurant.models import Booking, Menu


class MenuModelTests(TestCase):
    def test_menu_string_and_price(self):
        item = Menu.objects.create(title="Ice Cream", price="8.00", inventory=20)
        self.assertEqual(str(item), "Ice Cream : 8.00")
        self.assertEqual(Menu.objects.get(pk=item.pk).price, Decimal("8.00"))

    def test_zero_price_is_invalid(self):
        with self.assertRaises(ValidationError):
            Menu(title="Invalid", price=0).full_clean()


class BookingModelTests(TestCase):
    def test_booking_string(self):
        user = get_user_model().objects.create_user(username="guest", password="test-pass")
        booking = Booking.objects.create(user=user, name="Guest", no_of_guests=2,
                                         booking_date=timezone.now() + timedelta(days=1))
        self.assertIn("Guest (2)", str(booking))

    def test_guest_limit(self):
        with self.assertRaises(ValidationError):
            Booking(name="Guest", no_of_guests=21, booking_date=timezone.now()).full_clean()
