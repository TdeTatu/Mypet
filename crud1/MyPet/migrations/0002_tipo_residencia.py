# Generated by Django 5.1.3 on 2024-12-04 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("MyPet", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Tipo_Residencia",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("idTipo_Residencia", models.IntegerField()),
                ("Tipo_Residencia", models.CharField(max_length=14)),
            ],
        ),
    ]
