from django.db import IntegrityError, transaction
from django.shortcuts import render
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from .models import Booking, Menu
from .permissions import ReadOnlyOrStaff
from .serializers import BookingSerializer, MenuSerializer, UserSerializer


def home(request):
    return render(request, "restaurant/index.html")


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [ReadOnlyOrStaff]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title"]
    ordering_fields = ["price", "title", "id"]


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Booking.objects.select_related("user").all()
        return queryset if self.request.user.is_staff else queryset.filter(user=self.request.user)

    def _save(self, serializer, **kwargs):
        try:
            with transaction.atomic():
                serializer.save(**kwargs)
        except IntegrityError as exc:
            raise ValidationError({"booking_date": "You already have a booking at this time."}) from exc

    def perform_create(self, serializer):
        self._save(serializer, user=self.request.user)

    def perform_update(self, serializer):
        self._save(serializer)


class RegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(ObtainAuthToken):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"


class LogoutView(APIView):
    def post(self, request):
        if request.auth is not None:
            request.auth.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
