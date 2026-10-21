from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render

from objetos.models import Objeto


class LoginUsuarioView(LoginView):
    template_name = "usuarios/login.html"
    redirect_authenticated_user = True


def landing(request):
    """Página de inicio pública de PUPE."""
    activos = Objeto.objects.filter(estado=Objeto.Estado.ACTIVO)
    ctx = {
        "perdidos": activos.filter(tipo=Objeto.Tipo.PERDIDO).count(),
        "encontrados": activos.filter(tipo=Objeto.Tipo.ENCONTRADO).count(),
        "recuperados": Objeto.objects.filter(
            estado=Objeto.Estado.RECUPERADO
        ).count(),
        "recientes": activos[:3],
    }
    return render(request, "usuarios/landing.html", ctx)


@login_required
def inicio(request):
    return redirect("objetos:dashboard")


def registro(request):
    if request.user.is_authenticated:
        return redirect("objetos:dashboard")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("objetos:dashboard")
    else:
        form = UserCreationForm()

    return render(request, "usuarios/registro.html", {"form": form})