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
            cpf = form.cleaned_data['Cpf']
            nome = form.cleaned_data['Nome']
            data_nasc = form.cleaned_data['Data de nascimento']
            genero = form.cleaned_data['Gênero']
            endereco = form.cleaned_data['Endereço']
            tipo_residencia = form.cleaned_data['Tipo de residência']
            email = form.cleaned_data['Email']
            telefone = form.cleaned_data['Telefone']
            senha = form.cleaned_data['Senha']

            print(f'Cpf: {cpf}')
            print(f'Nome: {nome}')
            print(f'Data de Nascimento: {data_nasc}')
            print(f'Gênero: {genero}')
            print(f'Endereço: {endereco}')
            print(f'Tipo de residência: {tipo_residencia}')
            print(f'Email: {email}')
            print(f'Telefone: {telefone}')
            print(f'Senha: {senha}')

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

