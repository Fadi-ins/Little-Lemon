from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BookingViewSet, LoginView, LogoutView, MenuViewSet, RegistrationView, home

router = DefaultRouter()
router.register("menu", MenuViewSet, basename="menu")
router.register("booking/tables", BookingViewSet, basename="booking")

urlpatterns = [
    path("", home, name="restaurant-home"),
    path("api/", include(router.urls)),
    path("auth/users/", RegistrationView.as_view(), name="register"),
    path("auth/token/login/", LoginView.as_view(), name="login"),
    path("auth/token/logout/", LogoutView.as_view(), name="logout"),
]
