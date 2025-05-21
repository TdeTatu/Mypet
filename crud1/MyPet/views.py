# MyPet/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import CadastroUsarioForm, CadastroAnimalForm, AnimalModelForm
from .models import Animal, Perfil
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate


# A view 'index' não é mais definida aqui, pois a URL '/' (raiz)
# agora aponta diretamente para a view de login do Django no setup/urls.py.
# A view 'index' que usamos para o HTML da página de login é a padrão do Django.

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
            return redirect('index') # Redireciona para a página de login

        else:
            messages.error(request, 'Erro ao criar usuário! Verifique os dados.')
            print("Erros do formulário de cadastro:", form.errors)

    context = {
        'form': form
    }
    return render(request, "cadastro.html", context)

# Corrigido o caminho do template para "cadastro_pet.html"
def cadastro_pet(request):
    form = CadastroAnimalForm()
    context = {
        'form': form
    }
    return render(request, "cadastro_pet.html", context)

@login_required # Protege a página, exige login
def telaprincipal(request):
    return render(request, "telaprincipal.html")

@login_required # Protege a página, exige login
# Corrigido o caminho do template para "meuspets.html"
def meuspets(request):
    return render(request, "meuspets.html", {}) # Passe um contexto vazio para consistência

@login_required # Protege a página, exige login
# Corrigido o caminho do template para "acompanhamento.html"
def acompanhamento(request):
    return render(request, "acompanhamento.html", {}) # Passe um contexto vazio para consistência

@login_required # Protege a página, exige login
# Corrigido o caminho do template para "animal.html"
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


@login_required # Protege a página, exige login
# Corrigido o caminho do template para "muralpets.html"
def muralpets(request):
    return render(request, "muralpets.html", {}) # Passe um contexto vazio para consistência