from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect

from .forms import CadastroUsarioForm, CadastroAnimalForm, AnimalModelForm 
from .models import Animal
#, CadastroMonitorForm 

#from .models import Pessoa

# Create your views here.
def index(request):
    context = {
        'animais': Animal.objects.all()
    }
    return render(request, "index.html", context)

def cadastro(request):

    form = CadastroUsarioForm(request.POST or None)

    if str(request.method) == 'POST':
        if form.is_valid():
            form.send_mail()

            messages.success(request, 'Usuário cadastrado com sucesso!')
            form = CadastroUsarioForm()
        else:
            messages.error(request, 'Erro ao criar usuário!')


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

def animal(request):

    if str(request.user) != 'AnonymousUser':
        if str(request.method) == 'POST':
            form = AnimalModelForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()

                messages.sucess(request, 'Animal salvo com sucesso')
                form = AnimalModelForm()
            else:
                messages.error(request, 'Falha ao salvar animal')  
        else: 
            form = AnimalModelForm()
        context = {
            'form': form
        }
        return render(request, 'animal.html', context)
    else:
        return redirect('index')