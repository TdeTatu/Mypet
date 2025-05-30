# MyPet/models.py

from django.db import models
from stdimage.models import StdImageField
from django.contrib.auth.models import User

# SIGNALS
from django.db.models import signals
from django.template.defaultfilters import slugify

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cpf = models.CharField(max_length=14)
    data_nascimento = models.DateField()

    # Definição das opções para Gênero
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

    # Definição das opções para Tipo de Residência
    TIPO_RESIDENCIA_CHOICES = [
        ('casa', 'Casa'),
        ('apartamento', 'Apartamento'),
        ('condominio', 'Condomínio'),
        ('sitio_fazenda', 'Sítio / Fazenda'),
        ('outros', 'Outros'),
    ]
    tipo_residencia = models.CharField('Tipo de Residência', max_length=30, choices=TIPO_RESIDENCIA_CHOICES)

    # --- NOVA ALTERAÇÃO: Adiciona o campo foto_perfil ---
    foto_perfil = StdImageField(
        'Foto de Perfil',
        upload_to='perfis', # Pasta onde as fotos serão salvas (ex: media/perfis/)
        variations={'thumb': (128, 128, True)}, # Cria uma thumbnail de 128x128, cortando se necessário
        null=True, # Permite que o campo seja nulo no banco de dados
        blank=True # Permite que o campo seja deixado em branco no formulário
    )
    # --- FIM DA NOVA ALTERAÇÃO ---

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return f"Perfil de {self.user.username}"

class Base(models.Model):
    criado = models.DateTimeField('Data de criação', auto_now_add=True) # Mude de DateField para DateTimeField
    modificado = models.DateTimeField('Data de atualização', auto_now=True) # Mude de DateField para DateTimeField
    ativo = models.BooleanField('Ativo?', default=True)

    class Meta:
        abstract = True

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

    class Meta:
        verbose_name = 'Animal'
        verbose_name_plural = 'Animais'

    def __str__(self):
        return self.nome

def animal_pre_save(signal, instance, sender, **kwargs):
    instance.slug = slugify(instance.nome)

signals.pre_save.connect(animal_pre_save, sender=Animal)

# NOVO MODELO: VISITA
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

# --- NOVOS MODELOS PARA CHAT/MENSAGENS ---

class Conversa(Base):
    # O solicitante é quem inicia a conversa (interessado na adoção)
    solicitante = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='conversas_iniciadas', verbose_name='Solicitante')
    # O dono é o perfil do dono do animal
    dono = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='conversas_recebidas', verbose_name='Dono do Animal')
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, verbose_name='Animal Referência')
    ativa = models.BooleanField('Conversa Ativa?', default=True) # Para desativar conversas, se necessário

    class Meta:
        verbose_name = 'Conversa de Adoção'
        verbose_name_plural = 'Conversas de Adoção'
        # Garante que não haja conversas duplicadas entre os mesmos dois usuários sobre o mesmo animal
        unique_together = ('solicitante', 'dono', 'animal')
        ordering = ['-modificado'] # Conversas mais recentes primeiro

    def __str__(self):
        return f"Conversa entre {self.solicitante.user.username} e {self.dono.user.username} sobre {self.animal.nome}"

class Mensagem(models.Model):
    conversa = models.ForeignKey('Conversa', on_delete=models.CASCADE, related_name='mensagens')
    remetente = models.ForeignKey('Perfil', on_delete=models.CASCADE)
    conteudo = models.TextField(blank=True, null=True) # Conteúdo da mensagem pode ser nulo se for só mídia
    data_envio = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(default=False)

    # NOVO CAMPO: Para mídias (fotos e vídeos)
    media_file = models.FileField(upload_to='chat_media/', blank=True, null=True)

    # NOVO CAMPO: Para diferenciar o tipo de mídia no template (opcional, mas útil)
    MEDIA_TYPE_CHOICES = [
        ('image', 'Imagem'),
        ('video', 'Vídeo'),
    ]
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, blank=True, null=True)

    class Meta:
        ordering = ['data_envio']

    def __str__(self):
        if self.conteudo and self.media_file:
            return f"Mensagem de {self.remetente.user.username} (com anexo): {self.conteudo[:50]}..."
        elif self.conteudo:
            return f"Mensagem de {self.remetente.user.username}: {self.conteudo[:50]}..."
        elif self.media_file:
            return f"Mensagem de {self.remetente.user.username} (anexo: {self.media_file.name})"
        return f"Mensagem vazia de {self.remetente.user.username}"

    # Helper para verificar o tipo de mídia no template
    def is_image(self):
        return self.media_type == 'image'

    def is_video(self):
        return self.media_type == 'video'

    # Helper para obter a URL da mídia
    def get_media_url(self):
        if self.media_file:
            return self.media_file.url
        return None