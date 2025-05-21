# MyPet/urls.py

from django.urls import path
from . import views # Importa todas as views do seu aplicativo

urlpatterns = [
    # path('', views.index, name='index'), # Se você tiver uma view 'index' separada para a home
    path('cadastro/', views.cadastro, name='cadastro'),
    path('cadastro_pet/', views.cadastro_pet, name='cadastro_pet'),
    path('telaprincipal/', views.telaprincipal, name='telaprincipal'),
    path('meuspets/', views.meuspets, name='meuspets'),
    path('acompanhamento/', views.acompanhamento, name='acompanhamento'),
    path('muralpets/', views.muralpets, name='muralpets'),
    path('animal/', views.animal, name='animal'), # Verifique se essa URL é necessária/tem propósito claro
]