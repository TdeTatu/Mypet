# MyPet/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import CadastroUsarioForm, AnimalModelForm
from .models import Animal, Perfil
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm # Importe AuthenticationForm
from django.contrib.auth import login, logout, authenticate

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
            messages.success(request, 'Usuário cadastrado com sucesso! Faça login.')
            return redirect('index')
        else:
            messages.error(request, 'Erro ao criar usuário! Verifique os dados.')
            print("Erros do formulário de cadastro:", form.errors)
    context = {
        'form': form
    }
    return render(request, "cadastro.html", context)


@login_required
def cadastro_pet(request):
    if request.method == 'POST':
        form = AnimalModelForm(request.POST, request.FILES)
        if form.is_valid():
            animal = form.save(commit=False) # Não salva ainda no banco de dados

            print("\n--------------------------------------------------")
            print("DEBUG: Formulário de cadastro de animal VÁLIDO!")

            try:
                perfil_usuario = Perfil.objects.get(user=request.user)
                animal.owner = perfil_usuario # Associa o animal ao perfil do usuário
                animal.save() # Agora sim, salva o animal no banco de dados

                print(f"DEBUG: Animal '{animal.nome}' salvo com sucesso para o usuário '{request.user.username}' (Perfil ID: {perfil_usuario.id}).")
                print("--------------------------------------------------\n")

                messages.success(request, 'Animal cadastrado com sucesso!')
                return redirect('meuspets')

            except Perfil.DoesNotExist:
                messages.error(request, 'Erro: Seu perfil de usuário não foi encontrado. Por favor, cadastre seu perfil ou contate o suporte.')
                print(f"DEBUG: ERRO CRÍTICO - Perfil para o usuário {request.user.username} NÃO ENCONTRADO.")
                print("--------------------------------------------------\n")
                # Considere redirecionar para uma página de criação de perfil ou logout aqui
                return redirect('telaprincipal') # Ou para a página de criação de perfil
            except Exception as e:
                messages.error(request, f'Ocorreu um erro inesperado ao salvar o animal: {e}')
                print(f"DEBUG: ERRO INESPERADO ao salvar animal: {e}")
                print("--------------------------------------------------\n")
                return redirect('telaprincipal')

        else: # Formulário NÃO É VÁLIDO
            print("\n--------------------------------------------------")
            print("DEBUG: Formulário de cadastro de animal É INVÁLIDO!")
            print("DEBUG: Erros Detalhados do Formulário:", form.errors) # Mostra quais campos falharam e por quê
            print("DEBUG: Dados recebidos via POST:", request.POST) # Mostra o que o formulário enviou
            print("--------------------------------------------------\n")
            messages.error(request, 'Erro ao cadastrar animal! Verifique os dados e tente novamente.')

    else: # GET request (primeira vez que a página é acessada)
        form = AnimalModelForm()

    context = {
        'form': form
    }
    return render(request, "cadastro_pet.html", context)


@login_required
def telaprincipal(request):
    return render(request, "telaprincipal.html")

@login_required
def meuspets(request):
    pets_do_usuario = []
    try:
        perfil_usuario = Perfil.objects.get(user=request.user)
        pets_do_usuario = Animal.objects.filter(owner=perfil_usuario).order_by('nome')
    except Perfil.DoesNotExist:
        messages.info(request, 'Você ainda não possui um perfil cadastrado. Por favor, cadastre-se para ver seus pets.')

    context = {
        'pets': pets_do_usuario
    }
    return render(request, "meuspets.html", context)

@login_required
def acompanhamento(request):
    return render(request, "acompanhamento.html", {})

@login_required
def animal(request):
    messages.warning(request, 'Esta página "animal" pode ser redundante com "cadastro_pet". Verifique seu uso.')
    if request.method == 'POST':
        form = AnimalModelForm(request.POST, request.FILES)
        if form.is_valid():
            animal = form.save(commit=False)
            try:
                perfil_usuario = Perfil.objects.get(user=request.user)
                animal.owner = perfil_usuario
                animal.save()
                messages.success(request, 'Animal salvo com sucesso!')
                return redirect('meuspets')
            except Perfil.DoesNotExist:
                messages.error(request, 'Erro: Perfil do usuário não encontrado ao salvar animal.')
                return redirect('telaprincipal')
        else:
            messages.error(request, 'Falha ao salvar animal! Verifique os dados.')
            print("Erros do formulário Animal:", form.errors)
    else:
        form = AnimalModelForm()
    context = {
        'form': form
    }
    return render(request, 'animal.html', context)


@login_required
def muralpets(request):
    return render(request, "muralpets.html", {})

# Funções de Login/Logout
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password) # Use request no authenticate
            if user is not None:
                login(request, user)
                messages.info(request, f"Você está logado como {username}.")
                return redirect('telaprincipal')
            else:
                messages.error(request, "Nome de usuário ou senha inválidos.")
        else:
            messages.error(request, "Nome de usuário ou senha inválidos.")
    else:
        form = AuthenticationForm()
    return render(request, 'index.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, "Você foi desconectado com sucesso.")
    return redirect('index')