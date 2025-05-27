# setup/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from MyPet.views import user_login, user_logout # Importe suas views de login/logout
from django.contrib.auth import views as auth_views # Para usar as views de auth padrão do Django (logout)

urlpatterns = [
    # Sua URL de admin personalizada
    path('ControleSupremo/', admin.site.urls),

    # URLs do seu aplicativo MyPet
    path('', include('MyPet.urls')), # Inclui as URLs do seu aplicativo MyPet

    # Exemplo de URLs de login/logout (você pode tê-las no MyPet/urls.py também)
    # Se você está usando 'index' como LOGIN_URL, esta linha é importante
    path('login/', user_login, name='index'), # Redireciona para sua view de login
    path('logout/', user_logout, name='logout'), # Sua view de logout

    # Se você quiser usar as views de auth padrão do Django para logout:
    # path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
]

# Configuração para servir arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    #urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)