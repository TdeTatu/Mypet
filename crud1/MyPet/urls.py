# MyPet/urls.py

from django.urls import path
from . import views
from MyPet.views import user_login # Importe a view user_login aqui também, se ela estiver no MyPet/views.py

urlpatterns = [
    # Rota para a página inicial (login)
    path('', user_login, name='index'), # Adicionado para que a raiz do site aponte para o login
    
    path('cadastro/', views.cadastro, name='cadastro'),
    path('cadastro_pet/', views.cadastro_pet, name='cadastro_pet'),
    path('telaprincipal/', views.telaprincipal, name='telaprincipal'),
    path('meuspets/', views.meuspets, name='meuspets'),
    path('acompanhamento/', views.acompanhamento, name='acompanhamento'),
    path('muralpets/', views.muralpets, name='muralpets'),
    path('animal/', views.animal, name='animal'),
    path('editar_perfil/', views.editar_perfil, name='editar_perfil'),
    # --- NOVAS URLS ---
    path('detalhes_animal/<int:animal_id>/', views.detalhes_animal, name='detalhes_animal'),
    path('iniciar_chat/<int:dono_perfil_id>/<int:animal_id>/', views.iniciar_chat, name='iniciar_chat'),
    path('chats/', views.lista_chats, name='lista_chats'), # Nova URL para o menu de chats
    path('detalhes_chat/<int:conversa_id>/', views.detalhes_chat, name='detalhes_chat'), # Nova URL para o chat específico
    
    # URL para perfil público sem animal_id
    path('perfil_publico/<int:perfil_id>/', views.detalhes_perfil_publico, name='detalhes_perfil_publico'), 
    # URL para perfil público COM animal_id (para permitir iniciar chat a partir do animal)
    path('perfil_publico/<int:perfil_id>/<int:animal_id>/', views.detalhes_perfil_publico, name='detalhes_perfil_publico_com_animal'),
    # --- FIM DAS NOVAS URLS ---
]
