# MyPet/admin.py

from django.contrib import admin
from .models import Animal, Perfil

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'cpf', 'data_nascimento', 'genero', 'telefone', 'endereco', 'tipo_residencia')
    search_fields = ('user__username', 'cpf', 'telefone')
    list_filter = ('genero', 'tipo_residencia')

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('nome', 'especie', 'raca', 'porte', 'sexo', 'owner', 'dt_nascimento', 'idade', 'cor', 'tamanho', 'slug', 'criado', 'modificado', 'ativo')
    list_filter = ('especie', 'sexo', 'porte', 'ativo', 'owner')
    search_fields = ('nome', 'raca', 'owner__user__username')
    date_hierarchy = 'criado'