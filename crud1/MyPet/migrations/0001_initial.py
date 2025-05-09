# Generated by Django 5.2 on 2025-04-29 00:46

import stdimage.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Animal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado', models.DateField(auto_now_add=True, verbose_name='Data de criação')),
                ('modificado', models.DateField(auto_now_add=True, verbose_name='Data de atualização')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo?')),
                ('especie', models.CharField(max_length=100, verbose_name='Especie')),
                ('raca', models.CharField(max_length=100, verbose_name='Raça')),
                ('porte', models.CharField(max_length=100, verbose_name='Porte')),
                ('sexo', models.CharField(max_length=100, verbose_name='Sexo')),
                ('dt_nascimento', models.DateField(verbose_name='Data de nascimento')),
                ('imagem', stdimage.models.StdImageField(force_min_size=False, upload_to='animais', variations={'thumb': (124, 124)}, verbose_name='Imagem')),
                ('slug', models.SlugField(blank=True, editable=False, max_length=100, verbose_name='Slug')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
