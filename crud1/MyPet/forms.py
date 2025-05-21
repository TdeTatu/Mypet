# MyPet/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Animal, Perfil

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
            'dt_nascimento', 'imagem', 'idade', 'cor', 'tamanho'
        )
        widgets = {
            'dt_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'dt_nascimento': 'Data de Nascimento',
            'imagem': 'Foto do Animal',
            'idade': 'Idade (anos ou meses)',
        }