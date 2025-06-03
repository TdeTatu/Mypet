# MyPet/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import CadastroUsarioForm, AnimalModelForm, VisitaForm, EditarPerfilForm, MensagemForm
from .models import Animal, Perfil, Visita, Conversa, Mensagem, CompatibilidadeGemini # Importe CompatibilidadeGemini
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.db.models import Q # Para consultas complexas
from django.conf import settings # Para acessar a chave de API do settings.py
from django.utils import timezone # Para lidar com datas e horas

# Importe a biblioteca do Google AI
import google.generativeai as genai
import json # Para lidar com a resposta JSON do Gemini

# --- CONFIGURAÇÃO DA API DO GEMINI ---
# Certifique-se de que GEMINI_API_KEY está configurada no settings.py
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
else:
    print("AVISO: GEMINI_API_KEY não configurada no settings.py. As recomendações da IA não funcionarão.")

# --- FUNÇÃO DE CÁLCULO DE COMPATIBILIDADE (AGORA USANDO GEMINI) ---
async def get_gemini_compatibility_score(user_profile, animal):
    """
    Obtém a pontuação de compatibilidade e explicação do Gemini,
    usando cache para evitar chamadas repetitivas.
    """
    # Tenta buscar a pontuação em cache
    try:
        compatibilidade_cache = CompatibilidadeGemini.objects.get(
            perfil=user_profile,
            animal=animal
        )
        # Verifica se o cache é recente (ex: menos de 24 horas)
        # Ou se o perfil/animal não foi modificado desde a última avaliação
        # Para simplificar, vamos reavaliar se o cache tiver mais de 1 dia ou se o animal/perfil tiverem sido modificados.
        # Uma lógica mais robusta envolveria verificar 'modificado' timestamp.
        if (timezone.now() - compatibilidade_cache.modificado).days < 1:
            return compatibilidade_cache.pontuacao, compatibilidade_cache.explicacao

    except CompatibilidadeGemini.DoesNotExist:
        compatibilidade_cache = None # Não há cache, precisa gerar

    # Se não há cache ou o cache está desatualizado, chama o Gemini
    try:
        model = genai.GenerativeModel('gemini-1.5-flash') # Ou outro modelo Gemini, como 'gemini-pro'

        # Construa o prompt com as características do usuário e do animal
        prompt = f"""
        Você é um especialista em adoção de animais. Sua tarefa é avaliar a compatibilidade entre um perfil de usuário interessado em adotar e um animal disponível para adoção.
        Forneça uma pontuação de compatibilidade de 0 a 100 (onde 100 é a compatibilidade perfeita) e uma breve explicação.

        Características do Usuário:
        - Tipo de Residência: {user_profile.get_tipo_residencia_display()}
        - Nível de Atividade: {user_profile.get_nivel_atividade_usuario_display()}
        - Experiência com Animais: {user_profile.get_experiencia_animais_display()}
        - Possui Crianças: {'Sim' if user_profile.tem_criancas else 'Não'}
        - Faixa Etária das Crianças: {user_profile.idades_criancas if user_profile.tem_criancas else 'N/A'}
        - Possui Outros Animais: {'Sim' if user_profile.tem_outros_animais else 'Não'}
        - Tipo de Outros Animais: {user_profile.tipo_outros_animais if user_profile.tem_outros_animais else 'N/A'}
        - Temperamento dos Outros Animais: {user_profile.temperamento_outros_animais if user_profile.tem_outros_animais else 'N/A'}
        - Disposto a Necessidades Especiais: {'Sim' if user_profile.disposicao_necessidades_especiais else 'Não'}
        - Preferência de Espécie: {user_profile.get_preferencia_especie_animal_display()}
        - Preferência de Idade do Animal: {user_profile.get_preferencia_idade_animal_display()}
        - Preferência de Porte do Animal: {user_profile.get_preferencia_porte_animal_display()}

        Características do Animal ({animal.nome}):
        - Espécie: {animal.get_especie_display()}
        - Raça: {animal.raca}
        - Porte: {animal.get_porte_display()}
        - Idade: {animal.idade} ano(s) (se aplicável)
        - Nível de Energia: {animal.get_nivel_energia_display()}
        - Temperamento: {animal.temperamento}
        - Socialização com Crianças: {animal.get_socializacao_criancas_display()}
        - Socialização com Outros Animais: {animal.get_socializacao_outros_animais_display()}
        - Possui Necessidades Especiais: {'Sim' if animal.necessidades_especiais else 'Não'}
        - Descrição Necessidades Especiais: {animal.descricao_necessidades if animal.necessidades_especiais else 'N/A'}
        - Necessidade de Espaço: {animal.get_necessidade_espaco_display()}

        Formato da Resposta (JSON):
        {{
            "pontuacao": <int>,
            "explicacao": "<string>"
        }}
        """
        
        # Chamada síncrona para o Gemini (Django não suporta async views facilmente sem ASGI)
        # Para um ambiente de produção, considere usar Celery ou threads para chamadas de API longas.
        response = model.generate_content(prompt)
        
        # Tenta parsear a resposta JSON
        response_text = response.text.strip()
        # O Gemini pode retornar markdown code block, tente remover
        if response_text.startswith('```json') and response_text.endswith('```'):
            response_text = response_text[7:-3].strip()

        gemini_result = json.loads(response_text)
        
        pontuacao = gemini_result.get('pontuacao', 0)
        explicacao = gemini_result.get('explicacao', 'Nenhuma explicação fornecida.')

        # Salva ou atualiza o cache
        if compatibilidade_cache:
            compatibilidade_cache.pontuacao = pontuacao
            compatibilidade_cache.explicacao = explicacao
            compatibilidade_cache.save()
        else:
            CompatibilidadeGemini.objects.create(
                perfil=user_profile,
                animal=animal,
                pontuacao=pontuacao,
                explicacao=explicacao
            )
        
        return pontuacao, explicacao

    except Exception as e:
        print(f"Erro ao chamar a API do Gemini ou parsear resposta: {e}")
        # Retorna uma pontuação neutra/baixa em caso de erro
        return 0, "Erro ao gerar compatibilidade via IA."


def cadastro(request):
    form = CadastroUsarioForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
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
async def muralpets(request): # Alterado para async para permitir await na chamada Gemini
    # Tenta obter o perfil do usuário logado
    perfil_usuario = None
    try:
        perfil_usuario = Perfil.objects.get(user=request.user)
    except Perfil.DoesNotExist:
        messages.warning(request, 'Para melhores recomendações, complete seu perfil!')
        animais_para_adocao = Animal.objects.filter(disponivel_adocao=True, ativo=True).order_by('nome')
        context = {
            'animais': animais_para_adocao,
            'perfil_completo': False
        }
        return render(request, "muralpets.html", context)

    # Se o perfil do usuário existe, calcula a compatibilidade usando Gemini
    animais_disponiveis = Animal.objects.filter(disponivel_adocao=True, ativo=True)
    
    animais_com_pontuacao = []

    for animal in animais_disponiveis:
        # Chama a função assíncrona para obter a pontuação do Gemini
        pontuacao_gemini, explicacao_gemini = await get_gemini_compatibility_score(perfil_usuario, animal)
        
        # Anexa a pontuação e a explicação ao objeto animal temporariamente para ordenação e exibição
        animal.gemini_pontuacao = pontuacao_gemini
        animal.gemini_explicacao = explicacao_gemini
        
        animais_com_pontuacao.append((pontuacao_gemini, animal))

    # Ordena os animais pela pontuação de compatibilidade (do maior para o menor)
    animais_com_pontuacao.sort(key=lambda x: x[0], reverse=True)

    animais_ordenados = [animal for score, animal in animais_com_pontuacao]

    context = {
        'animais': animais_ordenados,
        'perfil_completo': True
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
        form = MensagemForm(request.POST, request.FILES) 
        if form.is_valid():
            conteudo = form.cleaned_data.get('conteudo')
            media_file = form.cleaned_data.get('media_file')

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
                conversa = Conversa.objects.create(
                    solicitante=solicitante_perfil,
                    dono=dono_perfil,
                    animal=animal
                )
                messages.info(request, f"Nova conversa iniciada com {dono_perfil.user.first_name if dono_perfil.user.first_name else dono_perfil.user.username} sobre {animal.nome}.")
            else:
                conversa = conversa_existente

            nova_mensagem = Mensagem(
                conversa=conversa,
                remetente=solicitante_perfil,
                conteudo=conteudo
            )

            if media_file:
                nova_mensagem.media_file = media_file
                if media_file.content_type.startswith('image'):
                    nova_mensagem.media_type = 'image'
                elif media_file.content_type.startswith('video'):
                    nova_mensagem.media_type = 'video'
                else:
                    nova_mensagem.media_type = None 

            nova_mensagem.save()

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
            context = {
                'dono_perfil': dono_perfil,
                'animal': animal,
                'form': form,
                'conversa_existente': conversa_existente
            }
            return render(request, 'iniciar_chat.html', context)
    else:
        form = MensagemForm()

    context = {
        'dono_perfil': dono_perfil,
        'animal': animal,
        'form': form,
        'conversa_existente': conversa_existente
    }
    return render(request, 'iniciar_chat.html', context)

# --- NOVO: Listar Chats/Solicitações ---
@login_required
def lista_chats(request):
    perfil_usuario = get_object_or_404(Perfil, user=request.user)

    conversas = Conversa.objects.filter(
        Q(solicitante=perfil_usuario) | Q(dono=perfil_usuario),
        ativa=True
    ).order_by('-modificado')

    for conversa in conversas:
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

    if not (conversa.solicitante == perfil_usuario or conversa.dono == perfil_usuario):
        messages.error(request, "Você não tem permissão para acessar esta conversa.")
        return redirect('lista_chats')

    if conversa.dono == perfil_usuario:
        conversa.mensagens.filter(remetente=conversa.solicitante, lida=False).update(lida=True)
    elif conversa.solicitante == perfil_usuario:
        conversa.mensagens.filter(remetente=conversa.dono, lida=False).update(lida=True)

    mensagens = conversa.mensagens.all()

    if request.method == 'POST':
        form = MensagemForm(request.POST, request.FILES) 
        if form.is_valid():
            conteudo = form.cleaned_data.get('conteudo')
            media_file = form.cleaned_data.get('media_file')

            if not conteudo and not media_file:
                messages.error(request, "A mensagem não pode ser vazia. Digite algo ou anexe uma foto/vídeo.")
                context = {
                    'conversa': conversa,
                    'mensagens': mensagens,
                    'form': form,
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
                if media_file.content_type.startswith('image'):
                    nova_mensagem.media_type = 'image'
                elif media_file.content_type.startswith('video'):
                    nova_mensagem.media_type = 'video'
                else:
                    nova_mensagem.media_type = None 

            nova_mensagem.save()
            messages.success(request, 'Mensagem enviada com sucesso!')

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

            return redirect('detalhes_chat', conversa_id=conversa.id)
        else:
            messages.error(request, 'Erro ao enviar mensagem. Verifique os dados do formulário.')
            print("Erros do formulário de mensagem em detalhes_chat:", form.errors)
            if conversa.solicitante == perfil_usuario:
                outro_participante = conversa.dono
            else:
                outro_participante = conversa.solicitante

            context = {
                'conversa': conversa,
                'mensagens': mensagens,
                'form': form,
                'perfil_usuario': perfil_usuario,
                'outro_participante': outro_participante,
            }
            return render(request, 'detalhes_chat.html', context)
    else:
        form = MensagemForm()

    if conversa.solicitante == perfil_usuario:
        outro_participante = conversa.dono
    else:
        outro_participante = conversa.solicitante

    context = {
        'conversa': conversa,
        'mensagens': mensagens,
        'form': form,
        'perfil_usuario': perfil_usuario,
        'outro_participante': outro_participante,
    }
    return render(request, 'detalhes_chat.html', context)

# --- NOVO: Visualizar Perfil Público de Outro Usuário ---
@login_required
def detalhes_perfil_publico(request, perfil_id, animal_id=None):
    perfil = get_object_or_404(Perfil, id=perfil_id)
    animal = None
    if animal_id:
        animal = get_object_or_404(Animal, id=animal_id)

    if perfil.user == request.user:
        messages.info(request, "Você está visualizando seu próprio perfil. Use 'Editar Perfil' para fazer alterações.")
        return redirect('editar_perfil')

    context = {
        'perfil': perfil,
        'animal': animal,
    }
    return render(request, 'detalhes_perfil_publico.html', context)
