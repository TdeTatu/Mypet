# MyPet/forms.py (ou o nome do seu aplicativo)

from django import forms
from django.core.mail.message import EmailMessage
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm # IMPORTANTE: Importar UserCreationForm

from .models import Animal # Certifique-se que Animal está importado se você usa AnimalModelForm

# Opções para os campos tipo select (mantidas como estão)
TIPOS_RESIDENCIA = [
    ('', 'Selecione o tipo de residência'),
    ('casa', 'Casa'),
    ('casa_grande', 'Casa Grande'),
    ('apartamento', 'Apartamento'),
]

GENEROS = [
    ('', 'Selecione o gênero'),
    ('masculino', 'Masculino'),
    ('feminino', 'Feminino'),
    ('outro', 'Outro'),
]

# CORREÇÃO PRINCIPAL: CadastroUsarioForm agora herda de UserCreationForm
class CadastroUsarioForm(UserCreationForm):
    cpf = forms.CharField(label='Cpf', max_length=100)
    # 'nome' será usado para o first_name do User
    nome = forms.CharField(label='Nome', max_length=100)
    data_de_nasc = forms.DateField(label='Data de nascimento', widget=forms.DateInput(attrs={'type': 'date'}))
    genero = forms.ChoiceField(label='Gênero', choices=GENEROS)
    endereco = forms.CharField(label='Endereço', max_length=100)
    tipo_residencia = forms.ChoiceField(label='Tipo de residência', choices=TIPOS_RESIDENCIA)
    # email é um campo padrão do User, mas é bom tê-lo aqui para personalização
    email = forms.EmailField(label='E-mail', max_length=100)
    telefone = forms.CharField(label='Telefone', max_length=100)
    # Não defina 'senha' ou 'password1', 'password2' aqui. UserCreationForm já os trata.

    class Meta(UserCreationForm.Meta): # Importante: Herdar da Meta de UserCreationForm
        model = User
        # Inclui os campos padrão do UserCreationForm (username, password, password2)
        # e adiciona seus campos extras
        fields = UserCreationForm.Meta.fields + ('email', 'cpf', 'nome', 'data_de_nasc', 'genero', 'endereco', 'tipo_residencia', 'telefone',)


class CadastroAnimalForm(forms.Form):
    especie = forms.ChoiceField(label='Espécie', choices=[('', 'Selecione a espécie')]) # Adicionei choices de exemplo
    raca = forms.ChoiceField(label='Raça', choices=[('', 'Selecione a raça')]) # Adicionei choices de exemplo
    porte = forms.ChoiceField(label='Porte do animal', choices=[('', 'Selecione o porte')]) # Adicionei choices de exemplo
    sexo = forms.ChoiceField(label='Sexo', choices=[('', 'Selecione o sexo'), ('M', 'Macho'), ('F', 'Fêmea')]) # Adicionei choices de exemplo
    dt_nascimento = forms.DateField(label='Data de nascimento', widget=forms.DateInput(attrs={'type': 'date'}))


class CadastroMonitorForm(forms.Form):
    cpf = forms.CharField(label='Cpf', max_length=100)
    nome = forms.CharField(label='Nome', max_length=100)
    data_de_nasc = forms.DateField(label='Data de nascimento', widget=forms.DateInput(attrs={'type': 'date'}))
    genero = forms.ChoiceField(label='Gênero', choices=GENEROS) # Reutilizando GENERO
    endereco = forms.CharField(label='Endereço', max_length=100)
    tipo_residencia = forms.ChoiceField(label='Tipo de residência', choices=TIPOS_RESIDENCIA) # Reutilizando TIPOS_RESIDENCIA
    email = forms.EmailField(label='E-mail', max_length=100)
    telefone = forms.CharField(label='Telefone', max_length=100)
    senha = forms.CharField(label='Senha', max_length=100, widget=forms.PasswordInput)


class ContatoForm(forms.Form):
    nome = forms.CharField(label='Nome', max_length=100, required=False)
    # email do contato precisa ser um campo do formulário para ser acessado via cleaned_data
    email_contato = forms.EmailField(label='E-mail', max_length=100, required=False) # Adicionei este campo

    def send_email(self):
        nome = self.cleaned_data.get('nome', 'Não informado') # Use .get para campos não obrigatórios
        email_contato = self.cleaned_data.get('email_contato', 'sem_email@exemplo.com') # Use o novo campo

        conteudo = f'Nome: {nome}\nEmail: {email_contato}\n'

        mail = EmailMessage(
            subject="Email enviado pelo sistema",
            body=conteudo,
            from_email='contato@seudominio.com.br',
            to=['contato@seudominio.com.br', ],
            headers={'Reply-To': email_contato}
        )
        mail.send()


class AnimalModelForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = ['nome', 'especie', 'raca', 'porte', 'sexo', 'dt_nascimento', 'imagem'] # Incluí 'imagem'
        widgets = {
            'dt_nascimento': forms.DateInput(attrs={'type': 'date'}) # Adicionei widget para data
        }