# MyPet/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('cadastro/', views.cadastro, name='cadastro'),
    path('cadastro_pet/', views.cadastro_pet, name='cadastro_pet'),
    path('telaprincipal/', views.telaprincipal, name='telaprincipal'),
    path('meuspets/', views.meuspets, name='meuspets'),
    path('acompanhamento/', views.acompanhamento, name='acompanhamento'),
    path('muralpets/', views.muralpets, name='muralpets'),
    path('animal/', views.animal, name='animal'), # Verifique se essa URL é necessária/tem propósito claro
    # --- NOVA URL: Editar Perfil ---
    path('editar_perfil/', views.editar_perfil, name='editar_perfil'),
    # --- FIM DA NOVA URL ---
]