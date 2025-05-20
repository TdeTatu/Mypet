# MyPet/urls.py

from django.urls import path

# Certifique-se que todas as views necessárias estão importadas aqui
from .views import index, cadastro, cadastro_pet, telaprincipal, meuspets, acompanhamento, animal

urlpatterns = [
    # REMOVIDA: path('', index, name= 'index'),
    # A URL raiz agora é tratada diretamente no setup/urls.py como a página de login

    path('cadastro/', cadastro, name= 'cadastro'),
    path('cadastro_pet/', cadastro_pet, name= 'cadastro_pet'),
    path('telaprincipal/', telaprincipal, name= 'telaprincipal'),
    path('meuspets/', meuspets, name= 'meuspets'),
    path('acompanhamento/', acompanhamento, name= 'acompanhamento'),
    path('animal/', animal, name= 'animal'),
]