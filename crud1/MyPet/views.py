from django.shortcuts import render
from django.contrib import messages

from .forms import CadastroUsarioForm, CadastroAnimalForm, CadastroMonitorForm

#from .models import Pessoa

# Create your views here.
def index(request):
    return render(request, "index.html")

def cadastro(request):

    form = CadastroUsarioForm(request.POST or None)

    if str(request.method) == 'POST':
        if form.is_valid():
            cpf = form.cleaned_data['cpf']
            nome = form.cleaned_data['nome']
            cpf = form.cleaned_data['']
            cpf = form.cleaned_data['']
            cpf = form.cleaned_data['']
            cpf = form.cleaned_data['']
            cpf = form.cleaned_data['']






    context = {
        'form': form
    }

    return render(request, "MyPet/cadastro.html", context)

def cadastro_pet(request):

    form = CadastroAnimalForm()

    context = {
        'form': form
    }


    return render(request, "MyPet/cadastro_pet.html", context) 

def telaprincipal(request):
    return render(request, "MyPet/telaprincipal.html")

def meuspets(request):
    return render(request, "MyPet/meuspets.html")

def acompanhamento(request):
    return render(request, "MyPet/acompanhamento.html")

