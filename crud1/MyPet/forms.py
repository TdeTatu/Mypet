# MyPet/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
# Importe as novas CHOICES junto com os modelos
from .models import Animal, Perfil, Visita, Conversa, Mensagem, \
    TEMPERAMENTO_ANIMAL_CHOICES, TEMPERAMENTO_OUTROS_ANIMAIS_SELECAO_CHOICES, FAIXA_ETARIA_CRIANCAS_CHOICES 

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

    foto_perfil = forms.ImageField(
        label='Foto de Perfil (Opcional)',
        required=False,
        widget=forms.FileInput
    )

    preferencia_especie_animal = forms.ChoiceField(
        label='Espécie de Animal Preferida',
        choices=Perfil.PREF_ESPECIE_CHOICES,
        initial='qualquer'
    )
    preferencia_idade_animal = forms.ChoiceField(
        label='Idade Preferencial do Animal',
        choices=Perfil.PREF_IDADE_CHOICES,
        initial='qualquer'
    )
    preferencia_porte_animal = forms.ChoiceField(
        label='Porte Preferencial do Animal',
        choices=Perfil.PREF_PORTE_CHOICES,
        initial='qualquer'
    )
    nivel_atividade_usuario = forms.ChoiceField(
        label='Seu Nível de Atividade',
        choices=Perfil.ATIVIDADE_USUARIO_CHOICES,
        initial='medio'
    )
    experiencia_animais = forms.ChoiceField(
        label='Experiência Prévia com Animais',
        choices=Perfil.EXPERIENCIA_CHOICES,
        initial='alguma'
    )
    
    tem_criancas = forms.BooleanField(
        label='Possui Crianças em Casa?',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # Campo idades_criancas agora é MultipleChoiceField
    idades_criancas = forms.MultipleChoiceField(
        label='Faixa Etária das Crianças (se houver)',
        choices=FAIXA_ETARIA_CRIANCAS_CHOICES, # Usando as CHOICES importadas
        required=False,
        widget=forms.CheckboxSelectMultiple, # Para permitir múltiplas seleções como checkboxes
        help_text='Selecione as faixas etárias das crianças em casa (múltiplas escolhas)'
    )
    
    tem_outros_animais = forms.BooleanField(
        label='Possui Outros Animais de Estimação?',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    tipo_outros_animais = forms.ChoiceField( # Mantido ChoiceField como no modelo para única seleção, se precisar de múltipla, seria MultipleChoiceField
        label='Tipo de Outros Animais (se houver)',
        choices=Perfil.TIPO_OUTROS_ANIMAIS_CHOICES,
        required=False,
    )
    
    # Campo temperamento_outros_animais agora é MultipleChoiceField
    temperamento_outros_animais = forms.MultipleChoiceField(
        label='Temperamento dos Outros Animais (se houver)',
        choices=TEMPERAMENTO_OUTROS_ANIMAIS_SELECAO_CHOICES, # Usando as CHOICES importadas
        required=False,
        widget=forms.CheckboxSelectMultiple, # Para permitir múltiplas seleções
        help_text='Selecione os temperamentos dos outros animais (múltiplas escolhas)'
    )
    
    disposicao_necessidades_especiais = forms.BooleanField(
        label='Disposto(a) a Adotar Animal com Necessidades Especiais?',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + (
            'nome', 'cpf', 'data_de_nasc', 'telefone', 'endereco', 'genero', 'tipo_residencia',
            'foto_perfil',
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

    # Sobrescreve o método clean para converter as listas de múltiplas escolhas em strings
    def clean(self):
        cleaned_data = super().clean()
        
        # Converte a lista de 'idades_criancas' em string separada por vírgula
        if 'idades_criancas' in cleaned_data and cleaned_data['idades_criancas']:
            cleaned_data['idades_criancas'] = ','.join(cleaned_data['idades_criancas'])
        else:
            cleaned_data['idades_criancas'] = ''

        # Converte a lista de 'temperamento_outros_animais' em string separada por vírgula
        if 'temperamento_outros_animais' in cleaned_data and cleaned_data['temperamento_outros_animais']:
            cleaned_data['temperamento_outros_animais'] = ','.join(cleaned_data['temperamento_outros_animais'])
        else:
            cleaned_data['temperamento_outros_animais'] = ''
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('nome', '')
        if commit:
            user.save()
            perfil_data = {
                'user': user,
                'cpf': self.cleaned_data['cpf'],
                'data_nascimento': self.cleaned_data['data_de_nasc'],
                'genero': self.cleaned_data['genero'],
                'telefone': self.cleaned_data['telefone'],
                'endereco': self.cleaned_data['endereco'],
                'tipo_residencia': self.cleaned_data['tipo_residencia'],
                'preferencia_especie_animal': self.cleaned_data['preferencia_especie_animal'],
                'preferencia_idade_animal': self.cleaned_data['preferencia_idade_animal'],
                'preferencia_porte_animal': self.cleaned_data['preferencia_porte_animal'],
                'nivel_atividade_usuario': self.cleaned_data['nivel_atividade_usuario'],
                'experiencia_animais': self.cleaned_data['experiencia_animais'],
                'tem_criancas': self.cleaned_data['tem_criancas'],
                'idades_criancas': self.cleaned_data['idades_criancas'], # Já é string separada por vírgula
                'tem_outros_animais': self.cleaned_data['tem_outros_animais'],
                'tipo_outros_animais': self.cleaned_data.get('tipo_outros_animais', ''),
                'temperamento_outros_animais': self.cleaned_data['temperamento_outros_animais'], # Já é string
                'disposicao_necessidades_especiais': self.cleaned_data['disposicao_necessidades_especiais']
            }
            
            foto_perfil_file = self.cleaned_data.get('foto_perfil')
            if foto_perfil_file:
                perfil_data['foto_perfil'] = foto_perfil_file

            Perfil.objects.create(**perfil_data)
        return user


class AnimalModelForm(forms.ModelForm):
    # ... (o campo temperamento continua definido aqui) ...
    temperamento = forms.MultipleChoiceField(
        label='Temperamento',
        choices=TEMPERAMENTO_ANIMAL_CHOICES,
        required=True, 
        widget=forms.CheckboxSelectMultiple,
        help_text='Selecione os temperamentos que melhor descrevem o animal (múltiplas escolhas)'
    )

    class Meta:
        model = Animal
        fields = (
            'nome', 'especie', 'raca', 'porte', 'sexo',
            'dt_nascimento', 'imagem', 'idade', 'cor', 'tamanho',
            'disponivel_adocao',
            'nivel_energia',
            # 'temperamento',  <- REMOVA ESTA LINHA
            'socializacao_criancas',
            'socializacao_outros_animais',
            'necessidades_especiais',
            'descricao_necessidades',
            'necessidade_espaco',
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
            'nivel_energia': 'Nível de Energia',
            'socializacao_criancas': 'Socializa com Crianças?',
            'socializacao_outros_animais': 'Socializa com Outros Animais?',
            'necessidades_especiais': 'Possui Necessidades Especiais?',
            'descricao_necessidades': 'Descrição das Necessidades Especiais',
            'necessidade_espaco': 'Necessidade de Espaço',
        }
    
    # Sobrescreve o __init__ para popular o MultipleChoiceField com valores existentes ao editar um animal
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.temperamento:
            # Converte a string separada por vírgulas de volta para uma lista
            self.initial['temperamento'] = self.instance.temperamento.split(',')

    # Sobrescreve o método save para converter a lista de volta para string antes de salvar
    def save(self, commit=True):
        # Pega a instância do modelo sem salvar no banco de dados ainda
        instance = super().save(commit=False)

        # Pega a LISTA de temperamentos já validada do cleaned_data
        temperamentos_list = self.cleaned_data.get('temperamento', [])
        
        # Converte a lista em uma string separada por vírgulas
        instance.temperamento = ','.join(temperamentos_list)

        # Salva a instância no banco de dados se commit for True
        if commit:
            instance.save()
            # self.save_m2m() # Necessário apenas se o formulário tivesse campos ManyToMany
        
        return instance


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
    # Campo idades_criancas agora é MultipleChoiceField
    idades_criancas = forms.MultipleChoiceField(
        label='Faixa Etária das Crianças (se houver)',
        choices=FAIXA_ETARIA_CRIANCAS_CHOICES, # Usando as CHOICES importadas
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text='Selecione as faixas etárias das crianças em casa (múltiplas escolhas)'
    )

    # Campo temperamento_outros_animais agora é MultipleChoiceField
    temperamento_outros_animais = forms.MultipleChoiceField(
        label='Temperamento dos Outros Animais (se houver)',
        choices=TEMPERAMENTO_OUTROS_ANIMAIS_SELECAO_CHOICES, # Usando as CHOICES importadas
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text='Selecione os temperamentos dos outros animais (múltiplas escolhas)'
    )

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
        )
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'tipo_outros_animais': forms.TextInput(attrs={'placeholder': 'Ex: Cachorro, gato, peixe'}),
        }
        labels = {
            'data_nascimento': 'Data de Nascimento',
            'foto_perfil': 'Foto de Perfil',
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
        }

    # Sobrescreve o __init__ para popular os MultipleChoiceFields com valores existentes
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance: # Se estiver editando um perfil existente
            # Converte a string separada por vírgulas de volta para uma lista
            if self.instance.idades_criancas:
                self.initial['idades_criancas'] = self.instance.idades_criancas.split(',')
            if self.instance.temperamento_outros_animais:
                self.initial['temperamento_outros_animais'] = self.instance.temperamento_outros_animais.split(',')

    # Sobrescreve o método clean para converter as listas de múltiplas escolhas em strings
    def clean(self):
        cleaned_data = super().clean()
        
        # Converte a lista de 'idades_criancas' em string separada por vírgula
        if 'idades_criancas' in cleaned_data and cleaned_data['idades_criancas']:
            cleaned_data['idades_criancas'] = ','.join(cleaned_data['idades_criancas'])
        else:
            cleaned_data['idades_criancas'] = ''

        # Converte a lista de 'temperamento_outros_animais' em string separada por vírgula
        if 'temperamento_outros_animais' in cleaned_data and cleaned_data['temperamento_outros_animais']:
            cleaned_data['temperamento_outros_animais'] = ','.join(cleaned_data['temperamento_outros_animais'])
        else:
            cleaned_data['temperamento_outros_animais'] = ''
        
        return cleaned_data


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