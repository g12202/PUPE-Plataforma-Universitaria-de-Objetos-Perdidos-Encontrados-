from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import MensajeForm, ObjetoForm
from .models import Mensaje, Objeto


def _contexto_base(request):
    return {
        "sin_leer": Mensaje.objects.filter(
            objeto__reportado_por=request.user, leido=False
        ).count()
    }


def _datos_mapa(queryset):
    return [
        {
            "id": o.pk,
            "titulo": o.titulo,
            "tipo": o.tipo,
            "categoria": o.get_categoria_display(),
            "lugar": o.lugar,
            "lat": o.latitud,
            "lng": o.longitud,
            "url": o.get_absolute_url(),
        }
        for o in queryset
        if o.tiene_ubicacion
    ]


@login_required
def dashboard(request):
    activos = Objeto.objects.filter(estado=Objeto.Estado.ACTIVO)
    stats = {
        "perdidos": activos.filter(tipo=Objeto.Tipo.PERDIDO).count(),
        "encontrados": activos.filter(tipo=Objeto.Tipo.ENCONTRADO).count(),
        "recuperados": Objeto.objects.filter(
            estado=Objeto.Estado.RECUPERADO
        ).count(),
        "mios": Objeto.objects.filter(reportado_por=request.user).count(),
    }
    por_categoria = (
        activos.values("categoria").annotate(total=Count("id")).order_by("-total")
    )
    nombres = dict(Objeto.Categoria.choices)
    categorias = [
        {
            "clave": c["categoria"],
            "nombre": nombres.get(c["categoria"], c["categoria"]),
            "total": c["total"],
        }
        for c in por_categoria
    ]
    ctx = {
        "stats": stats,
        "recientes": activos[:6],
        "categorias": categorias,
        "seccion": "dashboard",
        **_contexto_base(request),
    }
    return render(request, "objetos/dashboard.html", ctx)


@login_required
def buscar(request):
    qs = Objeto.objects.all()
    q = request.GET.get("q", "").strip()
    tipo = request.GET.get("tipo", "")
    categoria = request.GET.get("categoria", "")
    estado = request.GET.get("estado", "activo")

    if q:
        qs = qs.filter(
            Q(titulo__icontains=q)
            | Q(descripcion__icontains=q)
            | Q(lugar__icontains=q)
        )
    if tipo in Objeto.Tipo.values:
        qs = qs.filter(tipo=tipo)
    if categoria in Objeto.Categoria.values:
        qs = qs.filter(categoria=categoria)
    if estado in Objeto.Estado.values:
        qs = qs.filter(estado=estado)

    pagina = Paginator(qs, 9).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    ctx = {
        "pagina": pagina,
        "q": q,
        "tipo": tipo,
        "categoria": categoria,
        "estado": estado,
        "categorias": Objeto.Categoria.choices,
        "querystring": params.urlencode(),
        "seccion": "buscar",
        **_contexto_base(request),
    }
    return render(request, "objetos/buscar.html", ctx)


@login_required
def mapa(request):
    qs = Objeto.objects.filter(
        estado=Objeto.Estado.ACTIVO,
        latitud__isnull=False,
        longitud__isnull=False,
    )
    ctx = {
        "datos": _datos_mapa(qs),
        "centro": settings.CAMPUS_CENTER,
        "seccion": "mapa",
        **_contexto_base(request),
    }
    return render(request, "objetos/mapa.html", ctx)


@login_required
def reportar(request):
    inicial = {}
    if request.GET.get("tipo") in Objeto.Tipo.values:
        inicial["tipo"] = request.GET["tipo"]

    if request.method == "POST":
        form = ObjetoForm(request.POST, request.FILES)
        if form.is_valid():
            objeto = form.save(commit=False)
            objeto.reportado_por = request.user
            objeto.save()
            messages.success(request, "Tu reporte fue publicado.")
            return redirect(objeto)
    else:
        form = ObjetoForm(initial=inicial)

    ctx = {
        "form": form,
        "centro": settings.CAMPUS_CENTER,
        "titulo": "Reportar un objeto",
        "seccion": "reportar",
        **_contexto_base(request),
    }
    return render(request, "objetos/reportar.html", ctx)


@login_required
def editar(request, pk):
    objeto = get_object_or_404(Objeto, pk=pk, reportado_por=request.user)
    if request.method == "POST":
        form = ObjetoForm(request.POST, request.FILES, instance=objeto)
        if form.is_valid():
            form.save()
            messages.success(request, "Reporte actualizado.")
            return redirect(objeto)
    else:
        form = ObjetoForm(instance=objeto)
    ctx = {
        "form": form,
        "centro": settings.CAMPUS_CENTER,
        "titulo": "Editar reporte",
        "objeto": objeto,
        "seccion": "mis_reportes",
        **_contexto_base(request),
    }
    return render(request, "objetos/reportar.html", ctx)


@login_required
def detalle(request, pk):
    objeto = get_object_or_404(Objeto, pk=pk)
    es_dueno = objeto.reportado_por_id == request.user.id
    form = MensajeForm()

    if request.method == "POST" and not es_dueno:
        form = MensajeForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.objeto = objeto
            msg.autor = request.user
            msg.save()
            messages.success(request, "Mensaje enviado al reportante.")
            return redirect(objeto)

    ctx = {
        "objeto": objeto,
        "es_dueno": es_dueno,
        "form": form,
        "seccion": "mis_reportes" if es_dueno else "buscar",
        **_contexto_base(request),
    }
    return render(request, "objetos/detalle.html", ctx)


@login_required
@require_POST
def marcar_recuperado(request, pk):
    objeto = get_object_or_404(Objeto, pk=pk, reportado_por=request.user)
    objeto.estado = Objeto.Estado.RECUPERADO
    objeto.save(update_fields=["estado"])
    messages.success(request, "¡Qué bueno! Marcado como recuperado.")
    return redirect(objeto)


@login_required
@require_POST
def eliminar(request, pk):
    objeto = get_object_or_404(Objeto, pk=pk, reportado_por=request.user)
    objeto.delete()
    messages.success(request, "Reporte eliminado.")
    return redirect("objetos:mis_reportes")


@login_required
def mis_reportes(request):
    ctx = {
        "objetos": Objeto.objects.filter(reportado_por=request.user),
        "seccion": "mis_reportes",
        **_contexto_base(request),
    }
    return render(request, "objetos/mis_reportes.html", ctx)


@login_required
def mensajes(request):
    recibidos = Mensaje.objects.filter(
        objeto__reportado_por=request.user
    ).select_related("objeto", "autor")
    # Se marcan como leídos después de armar la lista.
    lista = list(recibidos)
    recibidos.filter(leido=False).update(leido=True)
    ctx = {
        "mensajes": lista,
        "seccion": "mensajes",
        "sin_leer": 0,
    }
    return render(request, "objetos/mensajes.html", ctx)
