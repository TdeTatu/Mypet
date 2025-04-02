from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.template import loader
from .models import Pessoa

# Create your views here.
def index(request):
    return render(request, "MyPet/index.html")

def cadastro(request):
    return render(request, "MyPet/cadastro.html")

def telaprincipal(request):
    return render(request, "MyPet/telaprincipal.html")

def meuspets(request):
    return render(request, "MyPet/meuspets.html")

def acompanhamento(request):
    return render(request, "MyPet/acompanhamento.html")

def Animal(request, pk):
    return render(request, "MyPet/Animal.html")

def error404(request, ex):
    template = loader.get_template('404.html')
    return HttpResponse(content=template.render(), content_type='text/html; charset=utf8', status=404)

def error500(request):
    template = loader.get_template('500.html')
    return HttpResponse(content=template.render(), content_type='text/html; charset=utf8', status=500)
    