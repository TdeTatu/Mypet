# MyPet/urls.py

from django.urls import path
from . import views
from MyPet.views import user_login # Importe a view user_login aqui, pois é a página inicial da app

urlpatterns = [
    # Rota para a página inicial (login) - Esta será a URL raiz ('/') e terá o nome 'index'.
    path('', user_login, name='index'), 
    
    path('cadastro/', views.cadastro, name='cadastro'),
    # CORRIGIDO: O nome da URL agora é 'cadastrar_pet' para corresponder ao HTML
    path('cadastro_pet/', views.cadastro_pet, name='cadastro_pet'),  
    path('telaprincipal/', views.telaprincipal, name='telaprincipal'),
    path('meuspets/', views.meuspets, name='meuspets'),
    path('acompanhamento/', views.acompanhamento, name='acompanhamento'),
    path('muralpets/', views.muralpets, name='muralpets'),
    path('animal/', views.animal, name='animal'), # Considere se 'animal/' deve ser uma lista ou detalhes de um animal específico
    path('editar_perfil/', views.editar_perfil, name='editar_perfil'),
    
    # --- URLS COM ID ---
    path('detalhes_animal/<int:animal_id>/', views.detalhes_animal, name='detalhes_animal'),
    path('iniciar_chat/<int:dono_perfil_id>/<int:animal_id>/', views.iniciar_chat, name='iniciar_chat'),
    path('chats/', views.lista_chats, name='lista_chats'), 
    path('detalhes_chat/<int:conversa_id>/', views.detalhes_chat, name='detalhes_chat'), 
    
    # URL para perfil público sem animal_id
    path('perfil_publico/<int:perfil_id>/', views.detalhes_perfil_publico, name='detalhes_perfil_publico'), 
    # URL para perfil público COM animal_id (para permitir iniciar chat a partir do animal)
    path('perfil_publico/<int:perfil_id>/<int:animal_id>/', views.detalhes_perfil_publico, name='detalhes_perfil_publico_com_animal'),
    # --- FIM DAS URLS ---
]