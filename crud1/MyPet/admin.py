# MyPet/admin.py

from django.contrib import admin
from .models import Animal, Perfil, Visita # Importe Visita aqui

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'cpf', 'data_nascimento', 'genero', 'telefone', 'endereco', 'tipo_residencia')
    search_fields = ('user__username', 'cpf', 'telefone')
    list_filter = ('genero', 'tipo_residencia')

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('nome', 'especie', 'raca', 'porte', 'sexo', 'owner', 'dt_nascimento', 'idade', 'cor', 'tamanho', 'slug', 'disponivel_adocao', 'criado', 'modificado', 'ativo') # Adicionado disponivel_adocao
    list_filter = ('especie', 'sexo', 'porte', 'disponivel_adocao', 'ativo', 'owner') # Adicionado disponivel_adocao
    search_fields = ('nome', 'raca', 'owner__user__username')
    date_hierarchy = 'criado'

# NOVO REGISTRO: VISITA
@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    list_display = ('animal', 'solicitante', 'data_visita', 'hora_visita', 'status', 'criado')
    list_filter = ('status', 'data_visita', 'animal__especie', 'solicitante__user__username')
    search_fields = ('animal__nome', 'solicitante__user__username', 'observacoes')
    date_hierarchy = 'data_visita'
    raw_id_fields = ('animal', 'solicitante') # Melhora a usabilidade para selecionar Animal e Solicitante