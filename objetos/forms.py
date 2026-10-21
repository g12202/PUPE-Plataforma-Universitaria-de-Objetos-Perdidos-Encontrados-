from django import forms

from .models import Mensaje, Objeto


class ObjetoForm(forms.ModelForm):
    class Meta:
        model = Objeto
        fields = [
            "tipo", "titulo", "categoria", "descripcion",
            "lugar", "fecha", "latitud", "longitud", "foto",
        ]
        widgets = {
            "tipo": forms.RadioSelect,
            "descripcion": forms.Textarea(attrs={"rows": 4}),
            "fecha": forms.DateInput(attrs={"type": "date"}),
            "latitud": forms.HiddenInput,
            "longitud": forms.HiddenInput,
            "foto": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }

    def clean_foto(self):
        foto = self.cleaned_data.get("foto")
        if foto and hasattr(foto, "size") and foto.size > 5 * 1024 * 1024:
            raise forms.ValidationError("La foto no debe pesar más de 5 MB.")
        return foto

    def clean_fecha(self):
        from django.utils import timezone

        fecha = self.cleaned_data["fecha"]
        if fecha > timezone.localdate():
            raise forms.ValidationError("La fecha no puede ser futura.")
        return fecha


class MensajeForm(forms.ModelForm):
    class Meta:
        model = Mensaje
        fields = ["texto"]
        widgets = {
            "texto": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Describe detalles que solo el dueño "
                                   "conocería, o cómo contactarte…",
                }
            )
        }
