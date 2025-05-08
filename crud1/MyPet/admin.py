from django.contrib import admin

from .models import Animal

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('nome', 'especie', 'raca', 'porte', 'sexo', 'dt_nascimento', 'slug', 'criado', 'modificado', 'ativo') 