from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import LoginUsuarioView, inicio, landing, registro

urlpatterns = [
    path("", landing, name="home"),
    path("login/", LoginUsuarioView.as_view(), name="login"),
    path("registro/", registro, name="registro"),
    path("inicio/", inicio, name="inicio"),
    path("logout/", LogoutView.as_view(), name="logout"),
]