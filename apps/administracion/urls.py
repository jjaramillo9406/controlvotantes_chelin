from django.urls import path, include
from apps.administracion import views

urlpatterns = [
    path('verificar_puestos/', views.verificar_votantes_view, name='verificar_votantes'),
    path('get_votantes_pendientes/', views.get_votantes_pendientes, name='get_votantes_pendientes'),
    path('get_puestos_votacion/', views.get_puestos_votacion, name='get_puestos_votacion'),
    path('save_puesto_votante/', views.save_puesto_votante, name='save_puesto_votante'),
    path('informe_lideres/', views.informe_lideres, name='informe_lideres'),
    path('informe_puestos/', views.informe_puestos, name='informe_puestos'),
    path('votantes_puesto_mesa/', views.get_votantes_puesto_mesa, name='votantes_puesto_mesa'),
]
