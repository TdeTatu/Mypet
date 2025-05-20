# MyPet/models.py (ou o nome do seu aplicativo)

from django.db import models
from stdimage.models import StdImageField
from django.contrib.auth.models import User


# Create your models here.
#SIGNALS
from django.db.models import signals
from django.template.defaultfilters import slugify

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cpf = models.CharField(max_length=14) # Ajustei para 14, caso inclua pontos/hífens
    data_nascimento = models.DateField()
    genero = models.CharField(max_length=20)
    telefone = models.CharField(max_length=20)
    endereco = models.CharField(max_length=200)
    tipo_residencia = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.user.username} - Perfil"

class Base(models.Model):
    criado = models.DateField('Data de criação', auto_now_add= True)
    modificado = models.DateField('Data de atualização', auto_now_add= True)
    ativo =models.BooleanField('Ativo?', default= True)

    class Meta:
        abstract= True

class Animal(Base):
    nome = models.CharField('Nome', max_length=100)
    especie = models.CharField('Especie', max_length=100)
    raca = models.CharField('Raça', max_length=100)
    porte = models.CharField('Porte', max_length=100)
    sexo = models.CharField('Sexo', max_length=100)
    dt_nascimento = models.DateField('Data de nascimento' )
    imagem = StdImageField('Imagem', upload_to = 'animais', variations={'thumb': (124, 124)})
    slug = models.SlugField('Slug', max_length=100, blank= True, editable= False)

    def __str__(self):
        return self.nome

def animal_pre_save(signal, instance, sender, **kwargs):
    instance.slug = slugify(instance.nome)

signals.pre_save.connect(animal_pre_save, sender= Animal)