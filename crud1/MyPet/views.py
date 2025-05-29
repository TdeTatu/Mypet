# MyPet/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import CadastroUsarioForm, AnimalModelForm, VisitaForm, EditarPerfilForm, MensagemForm # Importe MensagemForm
from .models import Animal, Perfil, Visita, Conversa, Mensagem # Importe os novos modelos
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.db.models import Q # Para consultas complexas

# Import para o envio de e-mails (ainda usado para notificação)
from django.core.mail import send_mail
from django.conf import settings

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
    perfil = get_object_or_404(Perfil, user=request.user)

    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('telaprincipal')
        else:
            messages.error(request, 'Erro ao atualizar o perfil. Verifique os dados.')
            print("Erros do formulário de edição de perfil:", form.errors)
    else:
        form = EditarPerfilForm(instance=perfil)

    context = {
        'form': form,
        'perfil': perfil
    }
    return render(request, "editar_perfil.html", context)

# --- NOVO: Detalhes do Animal e Perfil do Dono (Permite iniciar chat real) ---
@login_required
def detalhes_animal(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id)
    dono_perfil = animal.owner

    # Não permite que o dono do animal inicie um chat consigo mesmo
    pode_iniciar_chat = (request.user != dono_perfil.user)

    context = {
        'animal': animal,
        'dono_perfil': dono_perfil,
        'pode_iniciar_chat': pode_iniciar_chat,
    }
    return render(request, 'detalhes_animal.html', context)


# --- ATUALIZADO: Iniciar Chat (Agora cria uma Conversa e Mensagem) ---
@login_required
def iniciar_chat(request, dono_perfil_id, animal_id):
    solicitante_perfil = get_object_or_404(Perfil, user=request.user)
    dono_perfil = get_object_or_404(Perfil, id=dono_perfil_id)
    animal = get_object_or_404(Animal, id=animal_id)

    # Impede que o usuário converse consigo mesmo ou com seu próprio pet
    if solicitante_perfil == dono_perfil:
        messages.error(request, "Você não pode iniciar um chat com seu próprio perfil ou sobre seu próprio pet.")
        return redirect('detalhes_animal', animal_id=animal.id)

    # Verifica se já existe uma conversa ativa para este solicitante, dono e animal
    conversa_existente = Conversa.objects.filter(
        (Q(solicitante=solicitante_perfil) & Q(dono=dono_perfil)) |
        (Q(solicitante=dono_perfil) & Q(dono=solicitante_perfil)),
        animal=animal,
        ativa=True
    ).first()

    if request.method == 'POST':
        # IMPORTANTE: Incluir request.FILES para lidar com uploads de arquivos
        form = MensagemForm(request.POST, request.FILES) 
        if form.is_valid():
            conteudo = form.cleaned_data.get('conteudo')
            media_file = form.cleaned_data.get('media_file')

            # Uma mensagem deve ter conteúdo OU um arquivo de mídia
            if not conteudo and not media_file:
                messages.error(request, "A mensagem não pode ser vazia. Digite algo ou anexe uma foto/vídeo.")
                context = {
                    'dono_perfil': dono_perfil,
                    'animal': animal,
                    'form': form,
                    'conversa_existente': conversa_existente
                }
                return render(request, 'iniciar_chat.html', context)

            if not conversa_existente:
                # Se não existe, cria uma nova conversa
                conversa = Conversa.objects.create(
                    solicitante=solicitante_perfil,
                    dono=dono_perfil,
                    animal=animal
                )
                messages.info(request, f"Nova conversa iniciada com {dono_perfil.user.first_name if dono_perfil.user.first_name else dono_perfil.user.username} sobre {animal.nome}.")
            else:
                conversa = conversa_existente

            # Cria a nova mensagem
            nova_mensagem = Mensagem(
                conversa=conversa,
                remetente=solicitante_perfil,
                conteudo=conteudo
            )

            if media_file:
                nova_mensagem.media_file = media_file
                # Determinar o tipo de mídia (básico, pode ser melhorado com bibliotecas como python-magic)
                if media_file.content_type.startswith('image'):
                    nova_mensagem.media_type = 'image'
                elif media_file.content_type.startswith('video'):
                    nova_mensagem.media_type = 'video'
                else:
                    # Tratar outros tipos, ou ignorar, ou definir como 'other'
                    nova_mensagem.media_type = None # Ou 'other' dependendo da sua regra

            nova_mensagem.save()

            # Notifica o dono do animal por e-mail (opcional, mas boa prática)
            assunto = f"Nova Mensagem sobre {animal.nome} - MyPet"
            corpo_email = f"""
            Olá, {dono_perfil.user.first_name if dono_perfil.user.first_name else dono_perfil.user.username},

            Você recebeu uma nova mensagem de {solicitante_perfil.user.first_name if solicitante_perfil.user.first_name else solicitante_perfil.user.username}
            sobre o animal {animal.nome}.

            Para ver a mensagem e responder, acesse:
            {request.build_absolute_uri(f'/detalhes_chat/{conversa.id}/')}

            Atenciosamente,
            Equipe MyPet
            """
            try:
                send_mail(assunto, corpo_email, settings.DEFAULT_FROM_EMAIL, [dono_perfil.user.email], fail_silently=False)
                messages.success(request, f'Mensagem inicial enviada com sucesso para {dono_perfil.user.first_name if dono_perfil.user.first_name else dono_perfil.user.username} sobre {animal.nome}!')
            except Exception as e:
                messages.warning(request, f'Mensagem enviada, mas houve um erro ao enviar a notificação por e-mail: {e}')
                print(f"Erro ao enviar e-mail de notificação: {e}")

            return redirect('detalhes_chat', conversa_id=conversa.id)
        else:
            messages.error(request, 'Erro ao enviar mensagem. Verifique os dados do formulário.')
            print("Erros do formulário de mensagem em iniciar_chat:", form.errors)
            # A chave é re-renderizar a página com o formulário que contém os erros
            context = {
                'dono_perfil': dono_perfil,
                'animal': animal,
                'form': form, # Passa o formulário inválido de volta ao template
                'conversa_existente': conversa_existente
            }
            return render(request, 'iniciar_chat.html', context)
    else:
        # Se for GET, prepara o formulário para a primeira mensagem
        form = MensagemForm()

    context = {
        'dono_perfil': dono_perfil,
        'animal': animal,
        'form': form,
        'conversa_existente': conversa_existente # Para exibir uma nota se já existe conversa
    }
    return render(request, 'iniciar_chat.html', context)

# --- NOVO: Listar Chats/Solicitações ---
@login_required
def lista_chats(request):
    perfil_usuario = get_object_or_404(Perfil, user=request.user)

    # Conversas onde o usuário é o solicitante OU o dono
    # Usando Q para combinar as condições OR
    conversas = Conversa.objects.filter(
        Q(solicitante=perfil_usuario) | Q(dono=perfil_usuario),
        ativa=True # Apenas conversas ativas
    ).order_by('-modificado') # Ordena pelas mais recentes

    # Marcar mensagens não lidas
    for conversa in conversas:
        # Verifica se há mensagens não lidas enviadas pelo *outro* participante
        # para o perfil_usuario logado.
        conversa.tem_nao_lidas = Mensagem.objects.filter(
            conversa=conversa,
            lida=False
        ).exclude(remetente=perfil_usuario).exists()

    context = {
        'conversas': conversas,
        'perfil_usuario': perfil_usuario,
    }
    return render(request, 'lista_chats.html', context)

# --- NOVO: Detalhes do Chat e Resposta ---
@login_required
def detalhes_chat(request, conversa_id):
    perfil_usuario = get_object_or_404(Perfil, user=request.user)
    conversa = get_object_or_404(Conversa, id=conversa_id)

    # Garante que apenas os participantes da conversa possam acessá-la
    if not (conversa.solicitante == perfil_usuario or conversa.dono == perfil_usuario):
        messages.error(request, "Você não tem permissão para acessar esta conversa.")
        return redirect('lista_chats')

    # Marca as mensagens não lidas do *outro* participante como lidas
    # Se o usuário logado é o dono, marca as mensagens do solicitante como lidas
    if conversa.dono == perfil_usuario:
        conversa.mensagens.filter(remetente=conversa.solicitante, lida=False).update(lida=True)
    # Se o usuário logado é o solicitante, marca as mensagens do dono como lidas
    elif conversa.solicitante == perfil_usuario:
        conversa.mensagens.filter(remetente=conversa.dono, lida=False).update(lida=True)

    mensagens = conversa.mensagens.all() # Todas as mensagens da conversa

    if request.method == 'POST':
        # IMPORTANTE: Incluir request.FILES para lidar com uploads de arquivos
        form = MensagemForm(request.POST, request.FILES) 
        if form.is_valid():
            conteudo = form.cleaned_data.get('conteudo')
            media_file = form.cleaned_data.get('media_file')

            # Uma mensagem deve ter conteúdo OU um arquivo de mídia
            if not conteudo and not media_file:
                messages.error(request, "A mensagem não pode ser vazia. Digite algo ou anexe uma foto/vídeo.")
                # Se a mensagem é inválida, re-renderiza a página com o formulário e os erros
                context = {
                    'conversa': conversa,
                    'mensagens': mensagens,
                    'form': form, # Passa o formulário com os erros
                    'perfil_usuario': perfil_usuario,
                    'outro_participante': conversa.solicitante if perfil_usuario == conversa.dono else conversa.dono,
                }
                return render(request, 'detalhes_chat.html', context)


            nova_mensagem = Mensagem(
                conversa=conversa,
                remetente=perfil_usuario,
                conteudo=conteudo
            )

            if media_file:
                nova_mensagem.media_file = media_file
                # Determinar o tipo de mídia (básico, pode ser melhorado com bibliotecas)
                if media_file.content_type.startswith('image'):
                    nova_mensagem.media_type = 'image'
                elif media_file.content_type.startswith('video'):
                    nova_mensagem.media_type = 'video'
                else:
                    # Pode definir como 'other' ou deixar nulo se não for imagem/vídeo
                    nova_mensagem.media_type = None 

            nova_mensagem.save()
            messages.success(request, 'Mensagem enviada com sucesso!')

            # Opcional: Notificar o outro participante por e-mail sobre a nova mensagem
            # Identifica o destinatário
            destinatario_perfil = conversa.solicitante if perfil_usuario == conversa.dono else conversa.dono
            assunto_notificacao = f"Nova resposta na conversa sobre {conversa.animal.nome} - MyPet"
            corpo_notificacao = f"""
            Olá, {destinatario_perfil.user.first_name if destinatario_perfil.user.first_name else destinatario_perfil.user.username},

            Você recebeu uma nova mensagem de {perfil_usuario.user.first_name if perfil_usuario.user.first_name else perfil_usuario.user.username}
            na conversa sobre o animal {conversa.animal.nome}.

            Para ver a conversa completa e responder, acesse:
            {request.build_absolute_uri(f'/detalhes_chat/{conversa.id}/')}

            Atenciosamente,
            Equipe MyPet
            """
            try:
                send_mail(assunto_notificacao, corpo_notificacao, settings.DEFAULT_FROM_EMAIL, [destinatario_perfil.user.email], fail_silently=False)
            except Exception as e:
                messages.warning(request, f'Mensagem enviada, mas houve um erro ao enviar a notificação por e-mail: {e}')
                print(f"Erro ao enviar e-mail de notificação de resposta: {e}")

            return redirect('detalhes_chat', conversa_id=conversa.id) # Redireciona para atualizar as mensagens
        else:
            messages.error(request, 'Erro ao enviar mensagem. Verifique os dados do formulário.')
            print("Erros do formulário de mensagem em detalhes_chat:", form.errors)
            # Se o formulário for inválido, re-renderiza a página com o formulário e os erros
            # Identifica o outro participante da conversa para exibir seu perfil
            if conversa.solicitante == perfil_usuario:
                outro_participante = conversa.dono
            else:
                outro_participante = conversa.solicitante

            context = {
                'conversa': conversa,
                'mensagens': mensagens, # Para manter as mensagens existentes
                'form': form, # Passa o formulário com os erros de volta
                'perfil_usuario': perfil_usuario,
                'outro_participante': outro_participante,
            }
            return render(request, 'detalhes_chat.html', context)
    else:
        form = MensagemForm()

    # Identifica o outro participante da conversa para exibir seu perfil
    if conversa.solicitante == perfil_usuario:
        outro_participante = conversa.dono
    else:
        outro_participante = conversa.solicitante

    context = {
        'conversa': conversa,
        'mensagens': mensagens,
        'form': form,
        'perfil_usuario': perfil_usuario, # Perfil do usuário logado
        'outro_participante': outro_participante, # Perfil do outro usuário na conversa
    }
    return render(request, 'detalhes_chat.html', context)


# --- NOVO: Visualizar Perfil Público de Outro Usuário ---
@login_required
def detalhes_perfil_publico(request, perfil_id):
    # Apenas visualiza perfis que não sejam o do usuário logado
    perfil = get_object_or_404(Perfil, id=perfil_id)

    # Impede que o usuário veja seu próprio perfil por esta URL (use editar_perfil para isso)
    if perfil.user == request.user:
        messages.info(request, "Você está visualizando seu próprio perfil. Use 'Editar Perfil' para fazer alterações.")
        return redirect('editar_perfil') # Redireciona para a página de edição se for o próprio perfil

    context = {
        'perfil': perfil,
    }
    return render(request, 'detalhes_perfil_publico.html', context)