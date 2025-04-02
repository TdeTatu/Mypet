from django.contrib import admin
from .models import Animal, Pessoa, Monitor


# Register your models here.
admin.site.register(Animal)
admin.site.register(Pessoa)
admin.site.register(Monitor)