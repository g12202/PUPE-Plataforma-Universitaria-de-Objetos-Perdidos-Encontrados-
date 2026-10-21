from django.contrib import admin

from .models import Mensaje, Objeto


@admin.register(Objeto)
class ObjetoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "tipo", "categoria", "estado", "reportado_por", "fecha")
    list_filter = ("tipo", "estado", "categoria")
    search_fields = ("titulo", "descripcion", "lugar")


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ("objeto", "autor", "leido", "creado")
