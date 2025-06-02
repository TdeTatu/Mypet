# MyPet/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Animal, Perfil, Visita, Conversa, Mensagem # Importe os modelos atualizados

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

    # --- NOVOS CAMPOS DE PREFERÊNCIA PARA O CADASTRO INICIAL (adicionados aqui) ---
    preferencia_especie_animal = forms.ChoiceField(
        label='Espécie de Animal Preferida',
        choices=Perfil.PREF_ESPECIE_CHOICES, # Usando as choices definidas no modelo Perfil
        initial='qualquer'
    )
    preferencia_idade_animal = forms.ChoiceField(
        label='Idade Preferencial do Animal',
        choices=Perfil.PREF_IDADE_CHOICES, # Usando as choices definidas no modelo Perfil
        initial='qualquer'
    )
    preferencia_porte_animal = forms.ChoiceField(
        label='Porte Preferencial do Animal',
        choices=Perfil.PREF_PORTE_CHOICES, # Usando as choices definidas no modelo Perfil
        initial='qualquer'
    )
    nivel_atividade_usuario = forms.ChoiceField(
        label='Seu Nível de Atividade',
        choices=Perfil.ATIVIDADE_USUARIO_CHOICES, # Usando as choices definidas no modelo Perfil
        initial='medio'
    )
    experiencia_animais = forms.ChoiceField(
        label='Experiência Prévia com Animais',
        choices=Perfil.EXPERIENCIA_CHOICES, # Usando as choices definidas no modelo Perfil
        initial='alguma'
    )
    
    tem_criancas = forms.BooleanField(
        label='Possui Crianças em Casa?',
        required=False, # Não é obrigatório marcar, pois pode ser falso
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}) # Adiciona classe para estilização, se houver
    )
    idades_criancas = forms.CharField(
        label='Faixa Etária das Crianças (se houver)',
        max_length=100,
        required=False,
        help_text='Ex: 0-5, 6-12, 13+ ou deixe em branco se não houver'
    )
    
    tem_outros_animais = forms.BooleanField(
        label='Possui Outros Animais de Estimação?',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    tipo_outros_animais = forms.CharField(
        label='Tipo de Outros Animais (se houver)',
        max_length=100,
        required=False,
        help_text='Ex: Cachorro, gato, peixe'
    )
    temperamento_outros_animais = forms.CharField(
        label='Temperamento dos Outros Animais (se houver)',
        max_length=100,
        required=False,
        help_text='Ex: Dócil, dominante, brincalhão'
    )
    
    disposicao_necessidades_especiais = forms.BooleanField(
        label='Disposto(a) a Adotar Animal com Necessidades Especiais?',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    # --- FIM DOS NOVOS CAMPOS PARA CADASTRO INICIAL ---

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + (
            'nome', 'cpf', 'data_de_nasc', 'telefone', 'endereco', 'genero', 'tipo_residencia',
            # Adicionando os novos campos de preferência na meta fields para que sejam processados
            'preferencia_especie_animal', 'preferencia_idade_animal', 'preferencia_porte_animal',
            'nivel_atividade_usuario', 'experiencia_animais', 'tem_criancas', 'idades_criancas',
            'tem_outros_animais', 'tipo_outros_animais', 'temperamento_outros_animais',
            'disposicao_necessidades_especiais',
        )

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
                tipo_residencia=self.cleaned_data['tipo_residencia'],
                # --- Salvando os novos campos de preferência ---
                preferencia_especie_animal=self.cleaned_data['preferencia_especie_animal'],
                preferencia_idade_animal=self.cleaned_data['preferencia_idade_animal'],
                preferencia_porte_animal=self.cleaned_data['preferencia_porte_animal'],
                nivel_atividade_usuario=self.cleaned_data['nivel_atividade_usuario'],
                experiencia_animais=self.cleaned_data['experiencia_animais'],
                tem_criancas=self.cleaned_data['tem_criancas'],
                idades_criancas=self.cleaned_data.get('idades_criancas', ''), # Use .get() para campos não obrigatórios
                tem_outros_animais=self.cleaned_data['tem_outros_animais'],
                tipo_outros_animais=self.cleaned_data.get('tipo_outros_animais', ''),
                temperamento_outros_animais=self.cleaned_data.get('temperamento_outros_animais', ''),
                disposicao_necessidades_especiais=self.cleaned_data['disposicao_necessidades_especiais']
                # --- FIM do salvamento dos novos campos ---
            )
        return user


class AnimalModelForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = (
            'nome', 'especie', 'raca', 'porte', 'sexo',
            'dt_nascimento', 'imagem', 'idade', 'cor', 'tamanho',
            'disponivel_adocao',
            # --- NOVOS CAMPOS PARA ANIMAL ---
            'nivel_energia',
            'temperamento',
            'socializacao_criancas',
            'socializacao_outros_animais',
            'necessidades_especiais',
            'descricao_necessidades',
            'necessidade_espaco',
            # --- FIM DOS NOVOS CAMPOS ---
        )
        widgets = {
            'dt_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'descricao_necessidades': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'dt_nascimento': 'Data de Nascimento',
            'imagem': 'Foto do Animal',
            'idade': 'Idade (anos ou meses)',
            'disponivel_adocao': 'Disponível para Adoção?',
            # --- RÓTULOS PARA NOVOS CAMPOS DE ANIMAL ---
            'nivel_energia': 'Nível de Energia',
            'temperamento': 'Temperamento (ex: calmo, brincalhão)',
            'socializacao_criancas': 'Socializa com Crianças?',
            'socializacao_outros_animais': 'Socializa com Outros Animais?',
            'necessidades_especiais': 'Possui Necessidades Especiais?',
            'descricao_necessidades': 'Descrição das Necessidades Especiais',
            'necessidade_espaco': 'Necessidade de Espaço',
            # --- FIM DOS RÓTULOS ---
        }

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

class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = (
            'cpf',
            'data_nascimento',
            'genero',
            'telefone',
            'endereco',
            'tipo_residencia',
            'foto_perfil',
            # --- NOVOS CAMPOS DE PREFERÊNCIA PARA O PERFIL ---
            'preferencia_especie_animal',
            'preferencia_idade_animal',
            'preferencia_porte_animal',
            'nivel_atividade_usuario',
            'experiencia_animais',
            'tem_criancas',
            'idades_criancas',
            'tem_outros_animais',
            'tipo_outros_animais',
            'temperamento_outros_animais',
            'disposicao_necessidades_especiais',
            # --- FIM DOS NOVOS CAMPOS ---
        )
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'idades_criancas': forms.TextInput(attrs={'placeholder': 'Ex: 0-5, 6-12, 13+'}),
            'tipo_outros_animais': forms.TextInput(attrs={'placeholder': 'Ex: Cachorro, gato, peixe'}),
            'temperamento_outros_animais': forms.TextInput(attrs={'placeholder': 'Ex: Dócil, dominante, brincalhão'}),
        }
        labels = {
            'data_nascimento': 'Data de Nascimento',
            'foto_perfil': 'Foto de Perfil',
            # --- RÓTULOS PARA NOVOS CAMPOS DE PREFERÊNCIA ---
            'preferencia_especie_animal': 'Espécie de Animal Preferida',
            'preferencia_idade_animal': 'Idade Preferencial do Animal',
            'preferencia_porte_animal': 'Porte Preferencial do Animal',
            'nivel_atividade_usuario': 'Seu Nível de Atividade',
            'experiencia_animais': 'Experiência Prévia com Animais',
            'tem_criancas': 'Possui Crianças em Casa?',
            'idades_criancas': 'Faixa Etária das Crianças (se houver)',
            'tem_outros_animais': 'Possui Outros Animais de Estimação?',
            'tipo_outros_animais': 'Tipo de Outros Animais (se houver)',
            'temperamento_outros_animais': 'Temperamento dos Outros Animais (se houver)',
            'disposicao_necessidades_especiais': 'Disposto(a) a Adotar Animal com Necessidades Especiais?',
            # --- FIM DOS RÓTULOS ---
        }

class MensagemForm(forms.ModelForm):
    conteudo = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Digite sua mensagem...'}),
        required=False
    )
    media_file = forms.FileField(
        label='Anexar mídia (foto ou vídeo)',
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*,video/*'})
    )

    class Meta:
        model = Mensagem
        fields = ['conteudo', 'media_file']
