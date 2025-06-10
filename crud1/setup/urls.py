# setup/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from MyPet.views import user_logout # user_login será importado via include('MyPet.urls')
# from django.contrib.auth import views as auth_views # Descomente se for usar o LogoutView.as_view() padrão do Django

urlpatterns = [
    # Sua URL de admin personalizada
    path('ControleSupremo/', admin.site.urls),

    # Inclui as URLs do seu aplicativo MyPet.
    # A URL de login principal (name='index') deve vir de MyPet.urls.
    path('', include('MyPet.urls')), 

    # URL de logout. Use sua view ou a view padrão do Django.
    path('logout/', user_logout, name='logout'), 
    # Se quiser usar a view de logout padrão do Django, descomente a linha abaixo e comente a de cima:
    # path('logout_django/', auth_views.LogoutView.as_view(next_page='index'), name='logout_django'),
]

# Configuração para servir arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # Geralmente não necessário para STATIC_URL