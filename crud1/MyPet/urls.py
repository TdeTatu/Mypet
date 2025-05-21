# MyPet/urls.py

from django.urls import path

# Certifique-se que todas as views necessárias estão importadas aqui
from .views import cadastro, cadastro_pet, telaprincipal, meuspets, acompanhamento, animal, muralpets # Adicione 'muralpets' aqui

urlpatterns = [
    # A URL raiz agora é tratada diretamente no setup/urls.py como a página de login.
    # Não precisamos mais do path('', index, name='index'), aqui no app.

    path('cadastro/', cadastro, name= 'cadastro'),
    path('cadastro_pet/', cadastro_pet, name= 'cadastro_pet'),
    path('telaprincipal/', telaprincipal, name= 'telaprincipal'),
    path('meuspets/', meuspets, name= 'meuspets'),
    path('acompanhamento/', acompanhamento, name= 'acompanhamento'),
    path('animal/', animal, name= 'animal'),
    path('muralpets/', muralpets, name='muralpets'), # <--- NOVA URL AQUI
]