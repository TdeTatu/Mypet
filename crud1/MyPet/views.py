# MyPet/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import CadastroUsarioForm, AnimalModelForm, VisitaForm, EditarPerfilForm # Importe EditarPerfilForm
from .models import Animal, Perfil, Visita
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate

def cadastro(request):
    form = CadastroUsarioForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            # A lógica de salvar o Perfil já está no método save do forms.py
            form.save()
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
            animal = form.save(commit=False)

            print("\n--------------------------------------------------")
            print("DEBUG: Formulário de cadastro de animal VÁLIDO!")

            try:
                perfil_usuario = Perfil.objects.get(user=request.user)
                animal.owner = perfil_usuario
                animal.save()

                print(f"DEBUG: Animal '{animal.nome}' salvo com sucesso para o usuário '{request.user.username}' (Perfil ID: {perfil_usuario.id}).")
                print("--------------------------------------------------\n")

                messages.success(request, 'Animal cadastrado com sucesso!')
                return redirect('meuspets')

            except Perfil.DoesNotExist:
                messages.error(request, 'Erro: Seu perfil de usuário não foi encontrado. Por favor, cadastre seu perfil ou contate o suporte.')
                print(f"DEBUG: ERRO CRÍTICO - Perfil para o usuário {request.user.username} NÃO ENCONTRADO.")
                print("--------------------------------------------------\n")
                return redirect('telaprincipal')
            except Exception as e:
                messages.error(request, f'Ocorreu um erro inesperado ao salvar o animal: {e}')
                print(f"DEBUG: ERRO INESPERADO ao salvar animal: {e}")
                print("--------------------------------------------------\n")
                return redirect('telaprincipal')

        else:
            print("\n--------------------------------------------------")
            print("DEBUG: Formulário de cadastro de animal É INVÁLIDO!")
            print("DEBUG: Erros Detalhados do Formulário:", form.errors)
            print("DEBUG: Dados recebidos via POST:", request.POST)
            print("--------------------------------------------------\n")
            messages.error(request, 'Erro ao cadastrar animal! Verifique os dados e tente novamente.')

    else:
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
    perfil_usuario = None
    try:
        perfil_usuario = Perfil.objects.get(user=request.user)
    except Perfil.DoesNotExist:
        messages.error(request, 'Seu perfil de usuário não foi encontrado. Por favor, cadastre seu perfil para agendar visitas.')
        return redirect('telaprincipal')

    if request.method == 'POST':
        form = VisitaForm(request.POST, user_profile=perfil_usuario)
        if form.is_valid():
            visita = form.save(commit=False)
            visita.solicitante = perfil_usuario
            visita.save()
            messages.success(request, 'Visita agendada com sucesso!')
            return redirect('acompanhamento')
        else:
            print("\n--------------------------------------------------")
            print("DEBUG: Formulário de agendamento de visita INVÁLIDO!")
            print("DEBUG: Erros Detalhados do Formulário:", form.errors)
            print("DEBUG: Dados recebidos via POST:", request.POST)
            print("--------------------------------------------------\n")
            messages.error(request, 'Erro ao agendar visita! Verifique os dados.')
    else:
        form = VisitaForm(user_profile=perfil_usuario)

    visitas_agendadas = Visita.objects.filter(solicitante=perfil_usuario).order_by('data_visita', 'hora_visita')

    context = {
        'form': form,
        'visitas_agendadas': visitas_agendadas,
        'meus_pets': Animal.objects.filter(owner=perfil_usuario).order_by('nome')
    }
    return render(request, "acompanhamento.html", context)

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
    animais_para_adocao = Animal.objects.filter(disponivel_adocao=True, ativo=True).order_by('nome')
    context = {
        'animais': animais_para_adocao
    }
    return render(request, "muralpets.html", context)

# Funções de Login/Logout
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
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

# --- NOVA VIEW: Editar Perfil ---
@login_required
def editar_perfil(request):
    # Garante que só usuários logados possam acessar
    # Tenta pegar o Perfil do usuário logado, ou retorna um 404 se não existir
    perfil = get_object_or_404(Perfil, user=request.user)

    if request.method == 'POST':
        # Se for um POST, tenta salvar o formulário com os novos dados e arquivos (para foto)
        form = EditarPerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save() # Salva as alterações no perfil
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('telaprincipal') # Redireciona para a página principal
        else:
            messages.error(request, 'Erro ao atualizar o perfil. Verifique os dados.')
            print("Erros do formulário de edição de perfil:", form.errors) # Para depuração
    else:
        # Se for um GET, preenche o formulário com os dados existentes do perfil
        form = EditarPerfilForm(instance=perfil)

    context = {
        'form': form,
        'perfil': perfil # Passa o objeto perfil para o template, para exibir a foto atual
    }
    return render(request, "editar_perfil.html", context)