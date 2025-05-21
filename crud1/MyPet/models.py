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
    genero = models.CharField(max_length=20)
    telefone = models.CharField(max_length=20)
    endereco = models.CharField(max_length=200)
    tipo_residencia = models.CharField(max_length=30)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return f"Perfil de {self.user.username}"

class Base(models.Model):
    criado = models.DateField('Data de criação', auto_now_add=True)
    modificado = models.DateField('Data de atualização', auto_now=True)
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
    # O usuário que está agendando a visita (dono do animal)
    # ou o usuário que está solicitando a visita
    solicitante = models.ForeignKey(Perfil, on_delete=models.CASCADE, verbose_name='Solicitante da Visita', related_name='visitas_solicitadas')
    # O animal que será visitado
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, verbose_name='Animal a ser visitado', related_name='visitas')
    data_visita = models.DateField('Data da Visita')
    hora_visita = models.TimeField('Hora da Visita')
    observacoes = models.TextField('Observações', blank=True, null=True)
    # status da visita (e.g., 'pendente', 'confirmada', 'cancelada', 'realizada')
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
        ordering = ['data_visita', 'hora_visita'] # Ordena as visitas por data e hora

    def __str__(self):
        return f"Visita para {self.animal.nome} em {self.data_visita} às {self.hora_visita} (Solicitante: {self.solicitante.user.username})"