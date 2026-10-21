from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Objeto(models.Model):
    class Tipo(models.TextChoices):
        PERDIDO = "perdido", "Perdido"
        ENCONTRADO = "encontrado", "Encontrado"

    class Estado(models.TextChoices):
        ACTIVO = "activo", "Activo"
        RECUPERADO = "recuperado", "Recuperado"

    class Categoria(models.TextChoices):
        ELECTRONICO = "electronico", "Electrónicos"
        DOCUMENTOS = "documentos", "Documentos y credenciales"
        ROPA = "ropa", "Ropa y accesorios"
        MOCHILA = "mochila", "Mochilas y bolsos"
        LLAVES = "llaves", "Llaves"
        UTILES = "utiles", "Útiles y libros"
        OTRO = "otro", "Otro"

    tipo = models.CharField(max_length=12, choices=Tipo.choices)
    titulo = models.CharField("Título", max_length=100)
    descripcion = models.TextField("Descripción", max_length=1000)
    categoria = models.CharField(
        "Categoría", max_length=20, choices=Categoria.choices
    )
    lugar = models.CharField("Lugar", max_length=150)
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)
    fecha = models.DateField("Fecha", default=timezone.localdate)
    foto = models.FileField(
        "Foto",
        upload_to="objetos/%Y/%m/",
        blank=True,
        validators=[
            FileExtensionValidator(["jpg", "jpeg", "png", "webp", "gif"])
        ],
    )
    estado = models.CharField(
        max_length=12, choices=Estado.choices, default=Estado.ACTIVO
    )
    reportado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="objetos",
    )
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]

    def __str__(self):
        return f"{self.get_tipo_display()}: {self.titulo}"

    def get_absolute_url(self):
        return reverse("objetos:detalle", args=[self.pk])

    @property
    def tiene_ubicacion(self):
        return self.latitud is not None and self.longitud is not None


class Mensaje(models.Model):
    """Mensaje de una persona al reportante de un objeto."""

    objeto = models.ForeignKey(
        Objeto, on_delete=models.CASCADE, related_name="mensajes"
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mensajes_enviados",
    )
    texto = models.TextField("Mensaje", max_length=500)
    leido = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]

    def __str__(self):
        return f"{self.autor} → {self.objeto}"
