from django.shortcuts import render

from .models import Pessoa

# Create your views here.
def index(request):
    return render(request,"MyPet/index.html")