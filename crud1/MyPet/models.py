from django.db import models

# Create your models here.

#DADOS ANIMAL
class Animal(models.Model):
    idAnimal = models.IntegerField(null=False, blank=False)
    idade = models.DecimalField(null=False, blank=False, max_digits=2 , decimal_places=2)
    dt_nasc = models.DateField

class Status_Animal(models.Model):
    idStatus = models.IntegerField(null=False, blank=False)
    status = models.CharField(null=False, blank=False, max_length=20)

class Raca_gato(models.Model):
    idRaca_gato = models.IntegerField(null=False, blank=False)
    raca = models.CharField(null=False, blank=False, max_length=30)

class Raca_cachorro(models.Model):
    idRaca_cachorro = models.IntegerField(null=False, blank=False)
    raca = models.CharField(null=False, blank=False, max_length=30)

class Sexo(models.Model):
    idSexo = models.IntegerField(null=False, blank=False)
    sexo = models.CharField(null=False, blank=False, max_length=5)
    
class Porte(models.Model):
    idPorte = models.IntegerField(null=False, blank=False)
    porte = models.CharField(null=False, blank=False, max_length=30)
    
class Especie(models.Model):
    idEspecie = models.IntegerField(null=False, blank=False)
    especie = models.CharField(null=False, blank=False, max_length=40)
#///////////////////////

#DADOS PESSOA

class Pessoa(models.Model):
    cpf = models.CharField(max_length=11, null=False, blank=False, )
    Nome = models.CharField(null=False, blank=False, max_length=50)
    dt_nasc = models.DateField(null=False, blank=False)
    idade = models.IntegerField(null=False, blank=False)
    endereco = models.CharField(max_length=99, null=False, blank=False)
    telefone = models.CharField(max_length=11, null=False, blank=False)
    senha = models.CharField(max_length=20, null=False, blank=False)
    email = models.CharField(max_length=50, null=False, blank=False)
    fk_genero = models.ForeignKey("Genero", on_delete=models.CASCADE)
    fk_faixa_salarial = models.ForeignKey("Faixa_Salarial", on_delete=models.CASCADE)
    fk_tipo_residencia = models.ForeignKey("Tipo_Residencia", on_delete=models.CASCADE)

    #Propertys chaves estrangeiras da pessoa

    @property
    def genero(self):
        return self.fk_genero.idGenero
    
    @property
    def faixa_salarial(self):
        return self.fk_faixa_salarial.idFaixa_salarial
    
    @property
    def tipo_residencia(self):
        return self.fk_tipo_residencia.idTipo_Residencia

class Faixa_Salarial(models.Model):
    idFaixa_salarial = models.IntegerField(null=False, blank=False)
    faixa_salarial = models.CharField(null=False, blank=False, max_length=17)

class Genero(models.Model):
    idGenero = models.IntegerField(null=False,blank=False)
    genero = models.CharField(null=False, blank=False, max_length=6)

class Tipo_Residencia(models.Model):
    idTipo_Residencia = models.IntegerField(null=False, blank=False)
    Tipo_Residencia = models.CharField(null=False,blank=False,max_length=14)

#///////////////////////

#DADOS VISITA

class Visita(models.Model):
    idVisita = models.IntegerField(null=False, blank=False)
    dt_visita = models.DateField(null=False, blank=False)
    hr_visita = models.TimeField(null=False, blank=False)

class Status_visita(models.Model):
    idStatus_visista = models.IntegerField(null=False,blank=False)
    status_visita = models.CharField(null=False, blank=False, max_length=30)

class Monitor(models.Model):
    idMonitor = models.IntegerField(null=False, blank=False)
    monitor = models.CharField(max_length=30, null=False, blank=False)
    dt_nasc = models.DateField(null=False, blank=False)
    telefone = models.CharField(max_length=11, null=False, blank=False)
    email = models.CharField(max_length=20, null=False, blank=False)
    sexo = models.CharField(max_length=12, null=False, blank=False)

#///////////////////////

#DADOS ADOÇÃO

class Adocao(models.Model):
    idAdocao = models.IntegerField(null=False, blank=False)
    adocao = models.CharField(max_length=50, null=False, blank=False)
    dt_adocao = models.DateField(null=False, blank=False)

#///////////////////////



