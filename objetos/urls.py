from django.urls import path

from . import views

app_name = "objetos"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("buscar/", views.buscar, name="buscar"),
    path("mapa/", views.mapa, name="mapa"),
    path("reportar/", views.reportar, name="reportar"),
    path("mis-reportes/", views.mis_reportes, name="mis_reportes"),
    path("mensajes/", views.mensajes, name="mensajes"),
    path("objeto/<int:pk>/", views.detalle, name="detalle"),
    path("objeto/<int:pk>/editar/", views.editar, name="editar"),
    path("objeto/<int:pk>/recuperado/", views.marcar_recuperado, name="recuperado"),
    path("objeto/<int:pk>/eliminar/", views.eliminar, name="eliminar"),
]
