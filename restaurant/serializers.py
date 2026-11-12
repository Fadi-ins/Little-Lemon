from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import serializers

from .models import Booking, Menu

User = get_user_model()


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ["id", "title", "price", "inventory"]


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["id", "user", "name", "no_of_guests", "booking_date"]
        read_only_fields = ["user"]
        validators = []

    def validate_booking_date(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Choose a future date and time.")
        return value

    def validate(self, attrs):
        user = self.instance.user if self.instance else self.context["request"].user
        date = attrs.get("booking_date", getattr(self.instance, "booking_date", None))
        existing = Booking.objects.filter(user=user, booking_date=date)
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise serializers.ValidationError({"booking_date": "You already have a booking at this time."})
        return attrs


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]
        read_only_fields = ["id"]
        extra_kwargs = {"email": {"required": True, "allow_blank": False}}

    def validate(self, attrs):
        candidate = User(username=attrs.get("username"), email=attrs.get("email"))
        try:
            password_validation.validate_password(attrs["password"], candidate)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)}) from exc
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
