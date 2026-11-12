from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Menu(models.Model):
    title = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    inventory = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["id"]
        constraints = [models.CheckConstraint(condition=models.Q(price__gt=0), name="menu_price_positive")]

    def __str__(self):
        return f"{self.title} : {self.price}"


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    name = models.CharField(max_length=255)
    no_of_guests = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(20)])
    booking_date = models.DateTimeField()

    class Meta:
        ordering = ["booking_date", "id"]
        constraints = [
            models.UniqueConstraint(fields=["user", "booking_date"], name="unique_user_booking_time"),
            models.CheckConstraint(condition=models.Q(no_of_guests__gte=1, no_of_guests__lte=20), name="booking_guest_range"),
        ]

    def __str__(self):
        return f"{self.name} ({self.no_of_guests}) - {self.booking_date}"
