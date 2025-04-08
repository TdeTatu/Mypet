from django.shortcuts import render

#from .models import Pessoa

# Create your views here.
def index(request):
    return render(request, "index.html")

def cadastro(request):
    return render(request, "MyPet/cadastro.html")

def cadastro_pet(request):
    return render(request, "MyPet/cadastro_pet.html") 

def telaprincipal(request):
    return render(request, "MyPet/telaprincipal.html")

def meuspets(request):
    return render(request, "MyPet/meuspets.html")

def acompanhamento(request):
    return render(request, "MyPet/acompanhamento.html")

