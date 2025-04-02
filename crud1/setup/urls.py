
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404, handler500
from MyPet.views import index, cadastro, telaprincipal, meuspets, acompanhamento


urlpatterns = [
    path('ControleSupremo/', admin.site.urls),
    path('', index, name= 'index'),
    path('cadastro', cadastro),
    path('telaprincipal', telaprincipal),
    path('meuspets', meuspets),
    path('acompanhamento', acompanhamento),
]

handler404 = views.error404
handler500 = views.error500