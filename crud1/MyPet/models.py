from django.db import models
from django.contrib.auth.models import User
from stdimage.models import StdImageField

# SIGNALS (MANTIDO)
from django.db.models import signals
from django.template.defaultfilters import slugify

# --- NOVAS OPÇÕES DE ESCOLHA PADRONIZADAS (ADICIONADAS AQUI) ---
TEMPERAMENTO_ANIMAL_CHOICES = [
    ('calmo', 'Calmo'),
    ('brincalhao', 'Brincalhão'),
    ('timido', 'Tímido'),
    ('independente', 'Independente'),
    ('sociável_humanos', 'Sociável com Humanos'),
    ('sociável_animais', 'Sociável com Outros Animais'),
    ('agitado', 'Agitado'),
    ('ansioso_separacao', 'Ansiedade de Separação'),
    ('vocal', 'Vocal (Late/Mia Muito)'),
    ('destrutivo', 'Destrutivo'),
    ('ciumento', 'Ciumento'),
    ('protetor', 'Protetor'),
    ('medroso', 'Medroso'),
    ('reservado', 'Reservado'),
    ('adaptavel', 'Adaptável'),
    ('necessita_lideranca', 'Necessita Liderança/Experiência'),
    ('agressivo_animais', 'Agressivo com Outros Animais'), # Crítico
    ('agressivo_humanos', 'Agressivo com Humanos'), # Crítico
    ('agressivo_estranhos', 'Agressivo com Estranhos'), # Crítico
    ('reativo', 'Reativo (a estímulos)'),
    ('nao_avaliado', 'Não Avaliado/Informado'), # Manter, para IA considerar risco
    ('desconhecido', 'Desconhecido'), # Manter, para IA considerar risco
]

TEMPERAMENTO_OUTROS_ANIMAIS_SELECAO_CHOICES = [
    ('docil', 'Dócil'),
    ('dominante', 'Dominante'),
    ('brincalhao', 'Brincalhão'),
    ('competitivo', 'Competitivo'),
    ('reservado', 'Reservado'),
    ('ansioso', 'Ansioso'),
    ('reativo', 'Reativo'),
    ('nao_se_aplica', 'Não se Aplica (se não houver animais)'),
    ('nao_avaliado', 'Não Avaliado/Informado'),
]

FAIXA_ETARIA_CRIANCAS_CHOICES = [
    ('0_2', '0-2 anos (Bebês/Crianças de colo)'),
    ('3_5', '3-5 anos (Crianças pequenas)'),
    ('6_12', '6-12 anos (Crianças em idade escolar)'),
    ('13_17', '13-17 anos (Adolescentes)'),
    ('nao_se_aplica', 'Não se Aplica (Não possui crianças)'),
]
# --- FIM DAS NOVAS OPÇÕES DE ESCOLHA ---


# CLASSE BASE
class Base(models.Model):
    criado = models.DateTimeField('Data de criação', auto_now_add=True)
    modificado = models.DateTimeField('Data de atualização', auto_now=True)
    ativo = models.BooleanField('Ativo?', default=True)

    class Meta:
        abstract = True

class Perfil(Base):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cpf = models.CharField(max_length=14)
    data_nascimento = models.DateField()

    GENERO_CHOICES = [
        ('masculino', 'Masculino'),
        ('feminino', 'Feminino'),
        ('nao_binario', 'Não Binário'),
        ('outro', 'Outro'),
        ('prefiro_nao_dizer', 'Prefiro não dizer'),
    ]
    genero = models.CharField('Gênero', max_length=20, choices=GENERO_CHOICES)

    telefone = models.CharField(max_length=20)
    endereco = models.CharField(max_length=200)

    TIPO_RESIDENCIA_CHOICES = [
        ('casa', 'Casa'),
        ('apartamento', 'Apartamento'),
        ('condominio', 'Condomínio'),
        ('sitio_fazenda', 'Sítio / Fazenda'),
        ('outros', 'Outros'),
    ]
    tipo_residencia = models.CharField('Tipo de Residência', max_length=30, choices=TIPO_RESIDENCIA_CHOICES)

    foto_perfil = StdImageField(
        'Foto de Perfil',
        upload_to='perfis',
        variations={'thumb': (128, 128, True)},
        null=True,
        blank=True
    )

    PREF_PORTE_CHOICES = [
        ('pequeno', 'Pequeno'),
        ('medio', 'Médio'),
        ('grande', 'Grande'),
        ('gigante', 'Gigante'),
        ('qualquer', 'Qualquer Porte'),
    ]
    PREF_IDADE_CHOICES = [
        ('filhote', 'Filhote'),
        ('adulto', 'Adulto'),
        ('idoso', 'Idoso'),
        ('qualquer', 'Qualquer Idade'),
    ]
    ATIVIDADE_USUARIO_CHOICES = [
        ('baixo', 'Calmo/Sedentário'),
        ('medio', 'Moderado'),
        ('alto', 'Muito Ativo'),
    ]
    EXPERIENCIA_CHOICES = [
        ('nenhuma', 'Nenhuma'),
        ('alguma', 'Alguma'),
        ('muita', 'Muita'),
    ]
    TIPO_OUTROS_ANIMAIS_CHOICES = [
        ('cachorro', 'Cachorro'),
        ('gato', 'Gato'),
        ('outros', 'Outros'),
        ('nao_possui', 'Não Possui'),
    ]
    # TEMPERAMENTO_OUTROS_ANIMAIS_CHOICES (originalmente aqui, mas agora padronizada globalmente)
    PREF_ESPECIE_CHOICES = [
        ('cachorro', 'Cachorro'),
        ('gato', 'Gato'),
        ('passaro', 'Pássaro'),
        ('roedor', 'Roedor'),
        ('reptil', 'Réptil'),
        ('peixe', 'Peixe'),
        ('outros', 'Outros'),
        ('qualquer', 'Qualquer Espécie'),
    ]

    preferencia_especie_animal = models.CharField('Espécie Preferencial', max_length=100, choices=PREF_ESPECIE_CHOICES, default='qualquer')
    preferencia_idade_animal = models.CharField('Idade Preferencial do Animal', max_length=50, choices=PREF_IDADE_CHOICES, default='qualquer')
    preferencia_porte_animal = models.CharField('Porte Preferencial do Animal', max_length=50, choices=PREF_PORTE_CHOICES, default='qualquer')
    nivel_atividade_usuario = models.CharField('Seu Nível de Atividade', max_length=50, choices=ATIVIDADE_USUARIO_CHOICES, default='medio')
    experiencia_animais = models.CharField('Experiência Prévia com Animais', max_length=50, choices=EXPERIENCIA_CHOICES, default='alguma')
    
    tem_criancas = models.BooleanField('Possui Crianças em Casa?', default=False)
    
    # --- ALTERADO: idades_criancas para permitir múltiplas seleções padronizadas ---
    idades_criancas = models.CharField(
        'Faixa Etária das Crianças (se houver)',
        max_length=255, # Aumentar o tamanho para acomodar múltiplos valores separados por vírgula
        null=True,
        blank=True,
        choices=FAIXA_ETARIA_CRIANCAS_CHOICES, # Usando as novas escolhas
        help_text='Selecione as faixas etárias das crianças em casa (múltiplas escolhas, ex: 0-2 anos, 6-12 anos)'
    )
    
    tem_outros_animais = models.BooleanField('Possui Outros Animais de Estimação?', default=False)
    tipo_outros_animais = models.CharField('Tipo de Outros Animais (se houver)', max_length=100, null=True, blank=True, choices=TIPO_OUTROS_ANIMAIS_CHOICES)
    
    # --- ALTERADO: temperamento_outros_animais para permitir múltiplas seleções padronizadas ---
    temperamento_outros_animais = models.CharField(
        'Temperamento dos Outros Animais (se houver)',
        max_length=255, # Aumentar o tamanho para acomodar múltiplos valores separados por vírgula
        null=True,
        blank=True,
        choices=TEMPERAMENTO_OUTROS_ANIMAIS_SELECAO_CHOICES, # Usando as novas escolhas
        help_text='Selecione os temperamentos dos outros animais (múltiplas escolhas)'
    )
    
    disposicao_necessidades_especiais = models.BooleanField('Disposto(a) a Adotar Animal com Necessidades Especiais?', default=False)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return self.user.username

    # --- NOVOS MÉTODOS PARA EXIBIÇÃO DE MÚLTIPLAS ESCOLHAS ---
    def get_idades_criancas_display_list(self):
        """Retorna uma lista de rótulos legíveis para as faixas etárias das crianças."""
        if self.idades_criancas:
            selected_values = self.idades_criancas.split(',')
            display_list = []
            for val in selected_values:
                for choice_value, choice_label in FAIXA_ETARIA_CRIANCAS_CHOICES:
                    if choice_value == val:
                        display_list.append(choice_label)
                        break
            return display_list
        return []

    def get_temperamento_outros_animais_display_list(self):
        """Retorna uma lista de rótulos legíveis para os temperamentos de outros animais."""
        if self.temperamento_outros_animais:
            selected_values = self.temperamento_outros_animais.split(',')
            display_list = []
            for val in selected_values:
                for choice_value, choice_label in TEMPERAMENTO_OUTROS_ANIMAIS_SELECAO_CHOICES:
                    if choice_value == val:
                        display_list.append(choice_label)
                        break
            return display_list
        return []

class Animal(Base):
    owner = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE,
        verbose_name='Dono do Pet',
        related_name='animais',
        null=True,
        blank=True
    )
    nome = models.CharField('Nome', max_length=100)

    ESPECIE_CHOICES = [
        ('cachorro', 'Cachorro'),
        ('gato', 'Gato'),
        ('passaro', 'Pássaro'),
        ('roedor', 'Roedor'),
        ('reptil', 'Réptil'),
        ('peixe', 'Peixe'),
        ('outros', 'Outros'),
    ]
    PORTE_CHOICES = [
        ('pequeno', 'Pequeno'),
        ('medio', 'Médio'),
        ('grande', 'Grande'),
        ('gigante', 'Gigante'),
    ]
    SEXO_CHOICES = [
        ('macho', 'Macho'),
        ('femea', 'Fêmea'),
        ('nao_informado', 'Não Informado'),
    ]
    ENERGIA_CHOICES = [
        ('baixo', 'Baixo'),
        ('medio', 'Médio'),
        ('alto', 'Alto'),
    ]
    SOCIALIZACAO_CHOICES = [
        ('sim', 'Sim'),
        ('nao', 'Não'),
        ('depende', 'Depende'),
        ('nao_avaliado', 'Não Avaliado/Informado'),
    ]
    ESPACO_CHOICES = [
        ('pequeno', 'Pouco (apartamento)'),
        ('medio', 'Médio (casa sem quintal grande)'),
        ('grande', 'Grande (casa com quintal)'),
    ]

    especie = models.CharField('Espécie', max_length=100, choices=ESPECIE_CHOICES)
    raca = models.CharField('Raça', max_length=100)
    porte = models.CharField('Porte', max_length=100, choices=PORTE_CHOICES)
    sexo = models.CharField('Sexo', max_length=100, choices=SEXO_CHOICES)
    dt_nascimento = models.DateField('Data de nascimento')
    imagem = StdImageField('Imagem', upload_to='animais', variations={'thumb': (124, 124)})
    idade = models.IntegerField('Idade (em anos ou meses)', null=True, blank=True)
    cor = models.CharField('Cor', max_length=50, null=True, blank=True)
    tamanho = models.CharField('Tamanho', max_length=50, null=True, blank=True)
    slug = models.SlugField('Slug', max_length=100, blank=True, editable=False)
    disponivel_adocao = models.BooleanField('Disponível para Adoção?', default=False)

    nivel_energia = models.CharField('Nível de Energia', max_length=50, choices=ENERGIA_CHOICES, default='medio')
    
    # --- ALTERADO: temperamento para usar CHOICES padronizadas (ainda CharField, mas manipulado no form) ---
    temperamento = models.CharField(
        'Temperamento',
        max_length=255, # Aumentar o tamanho para acomodar múltiplos valores separados por vírgula
        choices=TEMPERAMENTO_ANIMAL_CHOICES, # Usando as novas escolhas
        help_text='Selecione os temperamentos que melhor descrevem o animal (múltiplas escolhas)'
    )
    
    socializacao_criancas = models.CharField('Socialização com Crianças', max_length=50, choices=SOCIALIZACAO_CHOICES, default='nao_avaliado')
    socializacao_outros_animais = models.CharField('Socialização com Outros Animais', max_length=50, choices=SOCIALIZACAO_CHOICES, default='nao_avaliado')
    necessidades_especiais = models.BooleanField('Possui Necessidades Especiais?', default=False)
    descricao_necessidades = models.TextField('Descrição das Necessidades Especiais', null=True, blank=True)
    necessidade_espaco = models.CharField('Necessidade de Espaço', max_length=50, choices=ESPACO_CHOICES, default='medio')

    class Meta:
        verbose_name = 'Animal'
        verbose_name_plural = 'Animais'

    def __str__(self):
        return self.nome

    # --- NOVO MÉTODO PARA EXIBIÇÃO DE MÚLTIPLAS ESCOLHAS ---
    def get_temperamento_display_list(self):
        """Retorna uma lista de rótulos legíveis para os temperamentos do animal."""
        if self.temperamento:
            selected_values = self.temperamento.split(',')
            display_list = []
            for val in selected_values:
                for choice_value, choice_label in TEMPERAMENTO_ANIMAL_CHOICES:
                    if choice_value == val:
                        display_list.append(choice_label)
                        break
            return display_list
        return []

# SIGNAL PARA ANIMAL (MANTIDO)
def animal_pre_save(signal, instance, sender, **kwargs):
    instance.slug = slugify(instance.nome)

signals.pre_save.connect(animal_pre_save, sender=Animal)

# MODELO VISITA (AJUSTADO PARA SUA VERSÃO MAIS RECENTE)
class Visita(Base):
    solicitante = models.ForeignKey(Perfil, on_delete=models.CASCADE, verbose_name='Solicitante da Visita', related_name='visitas_solicitadas')
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, verbose_name='Animal a ser visitado', related_name='visitas')
    data_visita = models.DateField('Data da Visita')
    hora_visita = models.TimeField('Hora da Visita')
    observacoes = models.TextField('Observações', blank=True, null=True)
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('realizada', 'Realizada'),
    ]
    status = models.CharField('Status da Visita', max_length=20, choices=STATUS_CHOICES, default='pendente')

    class Meta:
        verbose_name = 'Visita de Acompanhamento'
        verbose_name_plural = 'Visitas de Acompanhamento'
        ordering = ['data_visita', 'hora_visita']

    def __str__(self):
        return f"Visita para {self.animal.nome} em {self.data_visita} às {self.hora_visita} (Solicitante: {self.solicitante.user.username})"

# --- MODELOS PARA CHAT/MENSAGENS (AJUSTADOS PARA SUA VERSÃO MAIS RECENTE) ---

class Conversa(Base):
    solicitante = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='conversas_iniciadas', verbose_name='Solicitante')
    dono = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='conversas_recebidas', verbose_name='Dono do Animal')
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, verbose_name='Animal Referência')
    ativa = models.BooleanField('Conversa Ativa?', default=True)

    class Meta:
        verbose_name = 'Conversa de Adoção'
        verbose_name_plural = 'Conversas de Adoção'
        unique_together = ('solicitante', 'dono', 'animal')
        ordering = ['-modificado']

    def __str__(self):
        return f"Conversa entre {self.solicitante.user.username} e {self.dono.user.username} sobre {self.animal.nome}"

class Mensagem(Base):
    conversa = models.ForeignKey(Conversa, on_delete=models.CASCADE, related_name='mensagens')
    remetente = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='mensagens_enviadas')
    conteudo = models.TextField(blank=True, null=True)
    lida = models.BooleanField(default=False)

    media_file = models.FileField(upload_to='chat_media/', blank=True, null=True)

    MEDIA_TYPE_CHOICES = [
        ('image', 'Imagem'),
        ('video', 'Vídeo'),
        ('other', 'Outro'),
    ]
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, blank=True, null=True)

    class Meta:
        verbose_name = 'Mensagem'
        verbose_name_plural = 'Mensagens'
        ordering = ['criado']

    def __str__(self):
        if self.conteudo and self.media_file:
            return f"Mensagem de {self.remetente.user.username} (com anexo): {self.conteudo[:50]}..."
        elif self.conteudo:
            return f"Mensagem de {self.remetente.user.username}: {self.conteudo[:50]}..."
        elif self.media_file:
            return f"Mensagem de {self.remetente.user.username} (anexo: {self.media_file.name})"
        return f"Mensagem vazia de {self.remetente.user.username}"

    # Helpers
    def is_image(self):
        return self.media_type == 'image'

    def is_video(self):
        return self.media_type == 'video'

    def get_media_url(self):
        if self.media_file:
            return self.media_file.url
        return None

# --- NOVO MODELO PARA CACHE DE COMPATIBILIDADE DO GEMINI ---
class CompatibilidadeGemini(Base):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='compatibilidades_gemini')
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='compatibilidades_gemini')
    pontuacao = models.IntegerField('Pontuação de Compatibilidade', default=0)
    explicacao = models.TextField('Explicação da Compatibilidade', blank=True, null=True)

    class Meta:
        verbose_name = 'Compatibilidade Gemini'
        verbose_name_plural = 'Compatibilidades Gemini'
        unique_together = ('perfil', 'animal')

    def __str__(self):
        return f"Compatibilidade entre {self.perfil.user.username} e {self.animal.nome}: {self.pontuacao}"