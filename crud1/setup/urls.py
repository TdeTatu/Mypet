
from django.contrib import admin
from django.urls import path, include
from MyPet.views import index, cadastro, cadastro_pet, telaprincipal, meuspets, acompanhamento


urlpatterns = [
    path('ControleSupremo/', admin.site.urls),
    path('', include('MyPet.urls')),
    path('', index, name= 'index'),
    path('cadastro/', cadastro, name= 'cadastro'),
    path('cadastro_pet/', cadastro_pet, name= 'cadastro_pet'),
    path('telaprincipal/', telaprincipal, name= 'telaprincipal'),
    path('meuspets/', meuspets, name= 'meuspets'),
    path('acompanhamento/', acompanhamento, name= 'acompanhamento')
]

