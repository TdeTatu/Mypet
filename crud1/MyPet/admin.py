from django.contrib import admin

from .models import Animal
from .models import Perfil

admin.site.register(Perfil)


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('nome', 'especie', 'raca', 'porte', 'sexo', 'dt_nascimento', 'slug', 'criado', 'modificado', 'ativo') 