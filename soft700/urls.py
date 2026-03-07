from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('gestion/', include('apps.administracion.urls')),
    path('', include('apps.core.urls')),
]
