from django.db import models
from django.contrib.auth.models import User
from stdimage.models import StdImageField

# SIGNALS (MANTIDO)
from django.db.models import signals
from django.template.defaultfilters import slugify

# CLASSE BASE (AJUSTADA PARA SUA VERSÃO MAIS RECENTE)
class Base(models.Model):
    criado = models.DateTimeField('Data de criação', auto_now_add=True)
    modificado = models.DateTimeField('Data de atualização', auto_now=True)
    ativo = models.BooleanField('Ativo?', default=True) # MANTIDO SEU CAMPO ATIVO

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
    TEMPERAMENTO_OUTROS_ANIMAIS_CHOICES = [
        ('docil', 'Dócil'),
        ('dominante', 'Dominante'),
        ('brincalhao', 'Brincalhão'),
        ('nao_se_aplica', 'Não se Aplica'),
    ]
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
    idades_criancas = models.CharField('Faixa Etária das Crianças (se houver)', max_length=100, null=True, blank=True, help_text='Ex: 0-5, 6-12, 13+ ou "Não se aplica"')
    
    tem_outros_animais = models.BooleanField('Possui Outros Animais de Estimação?', default=False)
    tipo_outros_animais = models.CharField('Tipo de Outros Animais (se houver)', max_length=100, null=True, blank=True, choices=TIPO_OUTROS_ANIMAIS_CHOICES)
    temperamento_outros_animais = models.CharField('Temperamento dos Outros Animais (se houver)', max_length=100, null=True, blank=True, choices=TEMPERAMENTO_OUTROS_ANIMAIS_CHOICES)
    
    disposicao_necessidades_especiais = models.BooleanField('Disposto(a) a Adotar Animal com Necessidades Especiais?', default=False)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return self.user.username

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
    # O campo 'ativo' já está na sua classe Base agora, então não precisa duplicar aqui.

    nivel_energia = models.CharField('Nível de Energia', max_length=50, choices=ENERGIA_CHOICES, default='medio')
    temperamento = models.CharField('Temperamento', max_length=100, help_text='Ex: Calmo, brincalhão, tímido, independente, sociável.')
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

class Mensagem(Base): # Mudei para herdar de Base para ter 'criado' e 'modificado'
    conversa = models.ForeignKey(Conversa, on_delete=models.CASCADE, related_name='mensagens')
    remetente = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='mensagens_enviadas') # Adicionado related_name
    conteudo = models.TextField(blank=True, null=True)
    # data_envio removido, pois 'criado' da classe Base já serve para isso
    lida = models.BooleanField(default=False)

    media_file = models.FileField(upload_to='chat_media/', blank=True, null=True)

    MEDIA_TYPE_CHOICES = [
        ('image', 'Imagem'),
        ('video', 'Vídeo'),
        ('other', 'Outro'), # Adicionado 'other' para flexibilidade
    ]
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, blank=True, null=True)

    class Meta:
        verbose_name = 'Mensagem' # Adicionado verbose_name
        verbose_name_plural = 'Mensagens' # Adicionado verbose_name_plural
        ordering = ['criado'] # Alterado para 'criado'

    def __str__(self):
        if self.conteudo and self.media_file:
            return f"Mensagem de {self.remetente.user.username} (com anexo): {self.conteudo[:50]}..."
        elif self.conteudo:
            return f"Mensagem de {self.remetente.user.username}: {self.conteudo[:50]}..."
        elif self.media_file:
            return f"Mensagem de {self.remetente.user.username} (anexo: {self.media_file.name})"
        return f"Mensagem vazia de {self.remetente.user.username}"

    # Helpers (MANTIDOS)
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
        unique_together = ('perfil', 'animal') # Garante que cada par perfil-animal tenha apenas uma pontuação

    def __str__(self):
        return f"Compatibilidade entre {self.perfil.user.username} e {self.animal.nome}: {self.pontuacao}"
