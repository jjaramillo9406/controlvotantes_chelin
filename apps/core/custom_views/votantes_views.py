import io

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from apps.core.routines import masivo_votantes_routine

from apps.core.form import MasivoVotanteForm


@login_required(login_url=reverse_lazy('login'))
@require_http_methods(['GET', 'POST'])
def masivo_votantes(request):
    form = MasivoVotanteForm()
    if request.method == 'POST':
        form = MasivoVotanteForm(request.POST, request.FILES)
        if form.is_valid():
            data = io.BytesIO(form.cleaned_data['archivo'].read())
            errors = masivo_votantes_routine.load_votantes(data)
            if len(errors) > 0:
                for item in errors:
                    messages.error(request, item)
            else:
                messages.success(request, "Datos guardados correctamente")
                form = MasivoVotanteForm()
    return render(request, "votantes/masivo.html", {
        'form': form
    })