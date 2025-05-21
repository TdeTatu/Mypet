# MyPet/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Animal, Perfil, Visita # Importe Visita aqui

class CadastroUsarioForm(UserCreationForm):
    nome = forms.CharField(label='Nome Completo', max_length=255)
    cpf = forms.CharField(label='CPF', max_length=14, help_text='Formato: XXX.XXX.XXX-XX')
    data_de_nasc = forms.DateField(label='Data de Nascimento', widget=forms.DateInput(attrs={'type': 'date'}))
    genero = forms.CharField(label='Gênero', max_length=20)
    telefone = forms.CharField(label='Telefone', max_length=20)
    endereco = forms.CharField(label='Endereço', max_length=200)
    tipo_residencia = forms.CharField(label='Tipo de Residência', max_length=30)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('nome', 'cpf', 'data_de_nasc', 'genero', 'telefone', 'endereco', 'tipo_residencia',)

    def clean_cpf(self):
        cpf = self.cleaned_data['cpf']
        cpf_numerico = ''.join(filter(str.isdigit, cpf))
        if len(cpf_numerico) != 11:
            raise forms.ValidationError("CPF deve conter 11 dígitos.")
        return cpf


class AnimalModelForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = (
            'nome', 'especie', 'raca', 'porte', 'sexo',
            'dt_nascimento', 'imagem', 'idade', 'cor', 'tamanho',
            'disponivel_adocao'
        )
        widgets = {
            'dt_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'dt_nascimento': 'Data de Nascimento',
            'imagem': 'Foto do Animal',
            'idade': 'Idade (anos ou meses)',
            'disponivel_adocao': 'Disponível para Adoção?'
        }

# NOVO FORMULÁRIO: Agendamento de Visita
class VisitaForm(forms.ModelForm):
    class Meta:
        model = Visita
        fields = ['animal', 'data_visita', 'hora_visita', 'observacoes']
        widgets = {
            'data_visita': forms.DateInput(attrs={'type': 'date'}),
            'hora_visita': forms.TimeInput(attrs={'type': 'time'}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'animal': 'Selecione o Pet', # O animal será preenchido dinamicamente na view, mas o label é para o dropdown
            'data_visita': 'Data da Visita',
            'hora_visita': 'Hora da Visita',
            'observacoes': 'Observações (Opcional)',
        }

    def __init__(self, *args, **kwargs):
        # O 'user_profile' será passado da view para filtrar os animais
        user_profile = kwargs.pop('user_profile', None)
        super().__init__(*args, **kwargs)

        if user_profile:
            # Filtra os animais do usuário logado para o campo 'animal' do formulário
            self.fields['animal'].queryset = Animal.objects.filter(owner=user_profile).order_by('nome')
        else:
            # Se não houver user_profile (situação inesperada para esta view),
            # o queryset será vazio ou conterá todos os animais, dependendo da necessidade
            self.fields['animal'].queryset = Animal.objects.none() # Garante que nada é selecionável sem perfil