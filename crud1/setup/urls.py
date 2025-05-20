# setup/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

# Importar as views de autenticação padrão do Django
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('ControleSupremo/', admin.site.urls),

    # A URL vazia (raiz '/') agora aponta DIRETAMENTE para a view de login padrão do Django.
    # Ela usará seu template 'index.html' para exibir o formulário.
    path('', auth_views.LoginView.as_view(template_name='index.html'), name='index'),

    # Inclui as demais URLs do seu aplicativo MyPet, sem sobrescrever a raiz.
    # (Ex: /cadastro/, /telaprincipal/, etc.)
    path('', include('MyPet.urls')),

    # Mantém a URL de logout padrão do Django
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
]

# Apenas para servir arquivos de mídia em desenvolvimento
if settings.DEBUG:
    # CORREÇÃO AQUI: settings.MEDIA_ROOT estava como settings.A_ROOT na última vez
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)