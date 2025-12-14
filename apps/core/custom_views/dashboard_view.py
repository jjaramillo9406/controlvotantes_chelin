from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods


@login_required(login_url=reverse_lazy('login'))
@require_http_methods(['GET'])
def index(request):
    return render(request, 'dashboard/index.html')