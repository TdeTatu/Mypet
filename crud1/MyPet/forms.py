# MyPet/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Animal, Perfil, Visita # Importe Perfil (agora mais crucial para as choices)

class CadastroUsarioForm(UserCreationForm):
    nome = forms.CharField(label='Nome Completo', max_length=255)
    cpf = forms.CharField(label='CPF', max_length=14, help_text='Formato: XXX.XXX.XXX-XX')
    data_de_nasc = forms.DateField(label='Data de Nascimento', widget=forms.DateInput(attrs={'type': 'date'}))

    # --- INÍCIO DA CORREÇÃO ---
    # Redefinir genero e tipo_residencia para usar as choices do modelo Perfil
    # E para que o formulário saiba que são ChoiceFields
    genero = forms.ChoiceField(
        label='Gênero',
        choices=Perfil.GENERO_CHOICES, # Pega as choices diretamente do modelo Perfil
        widget=forms.Select # Garante que seja um dropdown
    )
    telefone = forms.CharField(label='Telefone', max_length=20)
    endereco = forms.CharField(label='Endereço', max_length=200)
    tipo_residencia = forms.ChoiceField( # Correção aqui
        label='Tipo de Residência',
        choices=Perfil.TIPO_RESIDENCIA_CHOICES, # Pega as choices diretamente do modelo Perfil
        widget=forms.Select # Garante que seja um dropdown
    )

    class Meta(UserCreationForm.Meta):
        model = User
        # Os campos 'genero' e 'tipo_residencia' SÃO declarados no formulário,
        # mas não devem ser incluídos na 'Meta.fields' que aponta para o modelo User.
        # Eles serão tratados no método 'save' personalizado.
        # Mantemos apenas os campos que realmente pertencem ao modelo User aqui.
        fields = UserCreationForm.Meta.fields + ('nome', 'cpf', 'data_de_nasc', 'telefone', 'endereco',) # Removido genero e tipo_residencia daqui

    def clean_cpf(self):
        cpf = self.cleaned_data['cpf']
        cpf_numerico = ''.join(filter(str.isdigit, cpf))
        if len(cpf_numerico) != 11:
            raise forms.ValidationError("CPF deve conter 11 dígitos.")
        return cpf

    # SOBRESCREVER O MÉTODO SAVE: ESSENCIAL PARA CRIAR O USUÁRIO E O PERFIL JUNTOS
    def save(self, commit=True):
        user = super().save(commit=False) # Salva o User, mas não no banco ainda
        user.first_name = self.cleaned_data.get('nome', '') # Adiciona o nome ao campo first_name do User
        if commit:
            user.save() # Agora sim, salva o User no banco de dados

            # Cria o Perfil associado ao User
            Perfil.objects.create(
                user=user,
                cpf=self.cleaned_data['cpf'],
                data_nascimento=self.cleaned_data['data_de_nasc'],
                genero=self.cleaned_data['genero'], # Pega o valor do ChoiceField
                telefone=self.cleaned_data['telefone'],
                endereco=self.cleaned_data['endereco'],
                tipo_residencia=self.cleaned_data['tipo_residencia'] # Pega o valor do ChoiceField
            )
        return user
    # --- FIM DA CORREÇÃO ---


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

# FORMULÁRIO: Agendamento de Visita (permanece inalterado)
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
            'animal': 'Selecione o Pet',
            'data_visita': 'Data da Visita',
            'hora_visita': 'Hora da Visita',
            'observacoes': 'Observações (Opcional)',
        }

    def __init__(self, *args, **kwargs):
        user_profile = kwargs.pop('user_profile', None)
        super().__init__(*args, **kwargs)

        if user_profile:
            self.fields['animal'].queryset = Animal.objects.filter(owner=user_profile).order_by('nome')
        else:
            self.fields['animal'].queryset = Animal.objects.none()
