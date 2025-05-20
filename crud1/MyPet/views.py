# MyPet/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import CadastroUsarioForm, CadastroAnimalForm, AnimalModelForm
from .models import Animal, Perfil
# Adicione este import para o decorador de login
from django.contrib.auth.decorators import login_required
# REMOVIDO: from django.contrib.auth.forms import AuthenticationForm
# REMOVIDO: from django.contrib.auth import login, logout, authenticate


# A view 'index' agora é apenas uma view normal, não a de login.
# Ela será usada se você criar uma nova URL para ela no futuro, ou se o LOGOUT_REDIRECT_URL
# apontar para ela e ela não for a mesma da view de login.
# Como agora a URL raiz '/' aponta para auth_views.LoginView, esta 'index'
# só será chamada se você criar uma URL específica para ela.
def index(request):
    # Se você quiser que o index.html tenha conteúdo diferente do login,
    # e que o login seja sempre na raiz, esta view não será chamada.
    # Se quiser que essa view seja a página inicial para LOGOUT_REDIRECT_URL,
    # então o HTML dela não deve conter o formulário de login.
    context = {
        'animais': Animal.objects.all() # Exemplo de conteúdo para a página inicial
    }
    return render(request, "index.html", context)


def cadastro(request):
    form = CadastroUsarioForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            user.first_name = form.cleaned_data.get('nome', '')
            user.save()

            Perfil.objects.create(
                user=user,
                cpf=form.cleaned_data['cpf'],
                data_nascimento=form.cleaned_data['data_de_nasc'],
                genero=form.cleaned_data['genero'],
                telefone=form.cleaned_data['telefone'],
                endereco=form.cleaned_data['endereco'],
                tipo_residencia=form.cleaned_data['tipo_residencia']
            )

            messages.success(request, 'Usuário cadastrado com sucesso!')
            # Redireciona para a página de login (que agora é a raiz)
            return redirect('index')

        else:
            messages.error(request, 'Erro ao criar usuário! Verifique os dados.')
            print("Erros do formulário de cadastro:", form.errors)

    context = {
        'form': form
    }
    return render(request, "cadastro.html", context)

def cadastro_pet(request):
    form = CadastroAnimalForm()
    context = {
        'form': form
    }
    return render(request, "MyPet/cadastro_pet.html", context)

@login_required # <--- Protege a página, exige login
def telaprincipal(request):
    return render(request, "telaprincipal.html")

def meuspets(request):
    return render(request, "MyPet/meuspets.html")

def acompanhamento(request):
    return render(request, "MyPet/acompanhamento.html")

@login_required # Protege a página, exige login
def animal(request):
    if request.method == 'POST':
        form = AnimalModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Animal salvo com sucesso!')
            form = AnimalModelForm()
        else:
            messages.error(request, 'Falha ao salvar animal! Verifique os dados.')
            print("Erros do formulário Animal:", form.errors)
    else:
        form = AnimalModelForm()
    context = {
        'form': form
    }
    return render(request, 'animal.html', context)