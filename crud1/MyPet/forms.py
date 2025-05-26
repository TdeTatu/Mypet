# MyPet/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Animal, Perfil, Visita # Importe Perfil, Visita

class CadastroUsarioForm(UserCreationForm):
    nome = forms.CharField(label='Nome Completo', max_length=255)
    cpf = forms.CharField(label='CPF', max_length=14, help_text='Formato: XXX.XXX.XXX-XX')
    data_de_nasc = forms.DateField(label='Data de Nascimento', widget=forms.DateInput(attrs={'type': 'date'}))

    genero = forms.ChoiceField(
        label='Gênero',
        choices=Perfil.GENERO_CHOICES,
        widget=forms.Select
    )
    telefone = forms.CharField(label='Telefone', max_length=20)
    endereco = forms.CharField(label='Endereço', max_length=200)
    tipo_residencia = forms.ChoiceField(
        label='Tipo de Residência',
        choices=Perfil.TIPO_RESIDENCIA_CHOICES,
        widget=forms.Select
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('nome', 'cpf', 'data_de_nasc', 'telefone', 'endereco',)

    def clean_cpf(self):
        cpf = self.cleaned_data['cpf']
        cpf_numerico = ''.join(filter(str.isdigit, cpf))
        if len(cpf_numerico) != 11:
            raise forms.ValidationError("CPF deve conter 11 dígitos.")
        return cpf

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('nome', '')
        if commit:
            user.save()
            Perfil.objects.create(
                user=user,
                cpf=self.cleaned_data['cpf'],
                data_nascimento=self.cleaned_data['data_de_nasc'],
                genero=self.cleaned_data['genero'],
                telefone=self.cleaned_data['telefone'],
                endereco=self.cleaned_data['endereco'],
                tipo_residencia=self.cleaned_data['tipo_residencia']
            )
        return user


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

# --- NOVO FORMULÁRIO: Editar Perfil ---
class EditarPerfilForm(forms.ModelForm):
    # Não precisamos redefinir campos de UserCreationForm como password
    # Este formulário é diretamente para o modelo Perfil.
    class Meta:
        model = Perfil
        # 'user' não precisa estar aqui, pois o perfil já está associado ao usuário logado
        fields = (
            'cpf',
            'data_nascimento',
            'genero',
            'telefone',
            'endereco',
            'tipo_residencia',
            'foto_perfil', # Inclua o novo campo de foto aqui
        )
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'data_nascimento': 'Data de Nascimento',
            'foto_perfil': 'Foto de Perfil',
        }