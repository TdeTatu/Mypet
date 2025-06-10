# MyPet/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import CadastroUsarioForm, AnimalModelForm, VisitaForm, EditarPerfilForm, MensagemForm
from .models import Animal, Perfil, Visita, Conversa, Mensagem, CompatibilidadeGemini, \
    TEMPERAMENTO_ANIMAL_CHOICES, TEMPERAMENTO_OUTROS_ANIMAIS_SELECAO_CHOICES, FAIXA_ETARIA_CRIANCAS_CHOICES 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.db.models import Q
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail

import google.generativeai as genai
import json
import logging 

from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

# --- CONFIGURAÇÃO DA API DO GEMINI ---
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY não configurada no settings.py. As recomendações da IA não funcionarão.")

# Função auxiliar para criar e usar o modelo Gemini de forma síncrona
def _generate_gemini_content_sync(prompt_text):
    """Função síncrona para criar o modelo Gemini e gerar conteúdo."""
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt_text)
    
    response_text = ""
    if response and hasattr(response, 'text') and response.text:
        response_text = response.text.strip()
        # Remove markdown code block if present
        if response_text.startswith('```json'):
            response_text = response_text[len('```json'):].strip()
            if response_text.endswith('```'):
                response_text = response_text[:-len('```')].strip()
        elif response_text.startswith('```'):
            response_text = response_text[len('```'):].strip()
            if response_text.endswith('```'):
                response_text = response_text[:-len('```')].strip()
    return response_text


### Função de Cálculo de Compatibilidade do Gemini

async def get_gemini_compatibility_score(user_profile, animal):
    """
    Obtém a pontuação de compatibilidade e explicação do Gemini,
    usando cache para evitar chamadas repetitivas.
    """
    compatibilidade_cache = None
    try:
        compatibilidade_cache = await sync_to_async(CompatibilidadeGemini.objects.get)(
            perfil=user_profile,
            animal=animal
        )
        if (timezone.now() - compatibilidade_cache.modificado).days < 1: 
            user_username = user_profile.user.username
            print(f"\n--- Resposta Gemini (CACHE) para {animal.nome} e {user_username} ---") 
            print(f"Pontuação: {compatibilidade_cache.pontuacao}")
            print(f"Explicação: {compatibilidade_cache.explicacao}")
            print("----------------------------------------------------\n")
            return compatibilidade_cache.pontuacao, compatibilidade_cache.explicacao

    except CompatibilidadeGemini.DoesNotExist:
        compatibilidade_cache = None
    except Exception as e:
        logger.error(f"Erro ao buscar compatibilidade no cache para {animal.nome} e {user_profile.user.username}: {e}", exc_info=True)
        compatibilidade_cache = None

    try:
        user_data = await sync_to_async(lambda: {
            'username': user_profile.user.username,
            'tipo_residencia': user_profile.get_tipo_residencia_display(),
            'nivel_atividade': user_profile.get_nivel_atividade_usuario_display(),
            'experiencia_animais': user_profile.get_experiencia_animais_display(),
            'tem_criancas': user_profile.tem_criancas,
            'idades_criancas_display': user_profile.get_idades_criancas_display_list(),
            'tem_outros_animais': user_profile.tem_outros_animais,
            'tipo_outros_animais': user_profile.tipo_outros_animais,
            'temperamento_outros_animais_display': user_profile.get_temperamento_outros_animais_display_list(),
            'disposicao_necessidades_especiais': user_profile.disposicao_necessidades_especiais,
            'preferencia_especie_animal_display': user_profile.get_preferencia_especie_animal_display(),
            'preferencia_porte_animal_display': user_profile.get_preferencia_porte_animal_display(),
            # --- CORREÇÃO APLICADA AQUI ---
            'preferencia_idade_animal_display': user_profile.get_preferencia_idade_animal_display(),
        })()

        animal_data = await sync_to_async(lambda: {
            'nome': animal.nome,
            'especie_display': animal.get_especie_display(),
            'raca': animal.raca,
            'porte_display': animal.get_porte_display(),
            'idade': animal.idade,
            'nivel_energia_display': animal.get_nivel_energia_display(),
            'temperamento_display': animal.get_temperamento_display_list(),
            'socializacao_criancas_display': animal.get_socializacao_criancas_display(),
            'socializacao_outros_animais_display': animal.get_socializacao_outros_animais_display(),
            'necessidades_especiais': animal.necessidades_especiais,
            'descricao_necessidades': animal.descricao_necessidades,
            'necessidade_espaco_display': animal.get_necessidade_espaco_display(),
        })()
        
        prompt = f"""
        Você é um especialista em adoção de animais. Sua tarefa é avaliar a compatibilidade entre um perfil de usuário interessado em adotar e um animal disponível para adoção.
        Forneça uma pontuação de compatibilidade de 0 a 100 (onde 100 é a compatibilidade perfeita) e uma breve explicação detalhada dos pontos fortes e fracos da compatibilidade.

        REGRAS DE COMPATIBILIDADE OBRIGATÓRIAS (PONTUAÇÃO DEVE SER 0 SE HOUVER CONFLITO):
        - Se o usuário possui crianças ('Sim') E o animal NÃO socializa com crianças ('Não'), a pontuação de compatibilidade DEVE ser 0.
        - Se o usuário possui outros animais ('Sim') E o animal NÃO socializa com outros animais ('Não'), a pontuação de compatibilidade DEVE ser 0.
        - Se o usuário tem animais com temperamento dominante ou competitivo (palavras-chave como 'dominante', 'competitivo', 'brigão') E o animal é tímido, medroso ou busca socialização, a pontuação deve ser baixa (20 ou menos).
        - Se o usuário NÃO está disposto a adotar animais com necessidades especiais ('Não') E o animal POSSUI necessidades especiais ('Sim'), a pontuação de compatibilidade DEVE ser 0.
        - Se o TEMPERAMENTO do animal contiver palavras como 'agressivo', 'reage mal', 'morde', 'não se dá', 'brigão', 'violento', 'confusento', 'hostil', 'perigoso', 'ataca', 'rosna', 'arredio', 'difícil', 'intolerante' ou similar, a pontuação DEVE ser 0, independentemente das condições do usuário (priorize a segurança).

        DIRETRIZES PARA PONTUAÇÃO (Considere esses fatores para a pontuação):
        1.  **Preferências do Usuário:**
            - **Espécie:** {user_data['preferencia_especie_animal_display']} (Quanto mais próximo, maior a pontuação. 'Qualquer Espécie' é neutro.)
            - **Idade:** {user_data['preferencia_idade_animal_display']} (Filhote, adulto, idoso. Compare com a idade real do animal.)
            - **Porte:** {user_data['preferencia_porte_animal_display']} (Pequeno, médio, grande, gigante. Compare com o porte do animal.)
        2.  **Estilo de Vida e Capacidade do Usuário:**
            - **Tipo de Residência:** {user_data['tipo_residencia']} (Compare com a 'Necessidade de Espaço' do animal.)
            - **Nível de Atividade:** {user_data['nivel_atividade']} (Compare com o 'Nível de Energia' do animal. Um usuário calmo e um animal muito ativo = baixa compatibilidade.)
            - **Experiência com Animais:** {user_data['experiencia_animais']} (Usuário com pouca experiência e animal desafiador = menor pontuação.)
        3.  **Temperamento e Socialização (Detalhes):**
            - O temperamento do animal ({', '.join(animal_data['temperamento_display'])}) e sua socialização com crianças ({animal_data['socializacao_criancas_display']}) e outros animais ({animal_data['socializacao_outros_animais_display']}) são cruciais.
            - Se o usuário tem outros animais, compare o temperamento deles ({', '.join(user_data['temperamento_outros_animais_display'])}) com a socialização do animal.
            - Procure por termos como 'carinhoso', 'dócil', 'amigável', 'brincalhão', 'sociável' no temperamento do animal para aumentar a pontuação.

        INFORMAÇÕES DO USUÁRIO ({user_data['username']}):
        - Tipo de Residência: {user_data['tipo_residencia']}
        - Nível de Atividade: {user_data['nivel_atividade']}
        - Experiência com Animais: {user_data['experiencia_animais']}
        - Possui Crianças: {'Sim' if user_data['tem_criancas'] else 'Não'}
        - Faixa Etária das Crianças: {', '.join(user_data['idades_criancas_display']) if user_data['tem_criancas'] and user_data['idades_criancas_display'] else 'N/A'}
        - Possui Outros Animais: {'Sim' if user_data['tem_outros_animais'] else 'Não'}
        - Tipo de Outros Animais: {user_data['tipo_outros_animais'] if user_data['tem_outros_animais'] else 'N/A'}
        - Temperamento dos Outros Animais: {', '.join(user_data['temperamento_outros_animais_display']) if user_data['tem_outros_animais'] and user_data['temperamento_outros_animais_display'] else 'N/A'}
        - Disposto a Necessidades Especiais: {'Sim' if user_data['disposicao_necessidades_especiais'] else 'Não'}
        - Preferência de Espécie: {user_data['preferencia_especie_animal_display']}
        - Preferência de Idade do Animal: {user_data['preferencia_idade_animal_display']}
        - Preferência de Porte do Animal: {user_data['preferencia_porte_animal_display']}

        INFORMAÇÕES DO ANIMAL ({animal_data['nome']}):
        - Espécie: {animal_data['especie_display']}
        - Raça: {animal_data['raca']}
        - Porte: {animal_data['porte_display']}
        - Idade: {animal_data['idade']} ano(s) (se aplicável)
        - Nível de Energia: {animal_data['nivel_energia_display']}
        - Temperamento: {', '.join(animal_data['temperamento_display'])}
        - Socialização com Crianças: {animal_data['socializacao_criancas_display']}
        - Socialização com Outros Animais: {animal_data['socializacao_outros_animais_display']}
        - Possui Necessidades Especiais: {'Sim' if animal_data['necessidades_especiais'] else 'Não'}
        - Descrição Necessidades Especiais: {animal_data['descricao_necessidades'] if animal_data['necessidades_especiais'] else 'N/A'}
        - Necessidade de Espaço: {animal_data['necessidade_espaco_display']}

        Formato da Resposta (JSON):
        {{
            "pontuacao": <int>,
            "explicacao": "<string>"
        }}
        """
        
        response_text = await sync_to_async(_generate_gemini_content_sync)(prompt)
        
        if not response_text:
            logger.error(f"Gemini API retornou uma resposta vazia após tratamento para o animal {animal_data['nome']}. Prompt: {prompt[:200]}...")
            return 0, "Erro: Resposta vazia da API do Gemini. Tente novamente mais tarde."

        try:
            gemini_result = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao parsear JSON da API do Gemini para o animal {animal_data['nome']}. Erro: {e}. Resposta bruta (pode ser truncada): {response_text[:500]}...")
            return 0, "Erro ao processar resposta da IA. Verifique sua chave API e logs."
        
        pontuacao = gemini_result.get('pontuacao', 0)
        explicacao = gemini_result.get('explicacao', 'Nenhuma explicação fornecida.')

        print(f"\n--- Resposta Gemini para {animal_data['nome']} e {user_data['username']} ---") 
        print(f"Prompt Enviado: {prompt}")
        print(f"Pontuação: {pontuacao}")
        print(f"Explicação: {explicacao}")
        print("----------------------------------------------------\n")

        if compatibilidade_cache:
            compatibilidade_cache.pontuacao = pontuacao
            compatibilidade_cache.explicacao = explicacao
            await sync_to_async(compatibilidade_cache.save)()
        else:
            await sync_to_async(CompatibilidadeGemini.objects.create)(
                perfil=user_profile,
                animal=animal,
                pontuacao=pontuacao,
                explicacao=explicacao
            )
        
        return pontuacao, explicacao

    except Exception as e:
        logger.error(f"Erro inesperado na função get_gemini_compatibility_score: {e}", exc_info=True)
        return 0, "Erro ao gerar compatibilidade via IA. Verifique sua chave API e logs."


### Views Comuns (Cadastro, Login, Logout, Perfil, Chat)

def cadastro(request):
    form = CadastroUsarioForm(request.POST or None)
    if request.method == 'POST':
        form = CadastroUsarioForm(request.POST, request.FILES) 
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário cadastrado com sucesso! Faça login.')
            return redirect('index')
        else:
            messages.error(request, 'Erro ao criar usuário! Verifique os dados.')
            print("Erros do formulário de cadastro:", form.errors)
    else:
        form = CadastroUsarioForm()
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
    messages.warning(request, 'Esta página "animal" parece ser redundante com "cadastro_pet". Considere remover ou renomear se não tiver um uso distinto. Ela pode ser usada para editar um animal existente, por exemplo.')
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
            except Exception as e:
                messages.error(request, f'Ocorreu um erro inesperado ao salvar o animal: {e}')
                return redirect('telaprincipal')
        else:
            messages.error(request, 'Falha ao salvar animal! Verifique os dados.')
    else:
        form = AnimalModelForm()
    context = {
        'form': form
    }
    return render(request, 'animal.html', context)


### View `muralpets` (Com Lógica de Compatibilidade)

@login_required
async def muralpets(request):
    perfil_usuario = None
    try:
        perfil_usuario = await sync_to_async(Perfil.objects.get)(user=request.user)
        user_profile_data = await sync_to_async(lambda p: {
            'username': p.user.username,
            'tem_criancas': p.tem_criancas,
            'disposicao_necessidades_especiais': p.disposicao_necessidades_especiais,
            'tem_outros_animais': p.tem_outros_animais,
            'preferencia_especie_animal': p.preferencia_especie_animal,
            'preferencia_porte_animal': p.preferencia_porte_animal,
            'temperamento_outros_animais_raw': p.temperamento_outros_animais.lower().split(',') if p.temperamento_outros_animais else [],
            'preferencia_especie_animal_display': p.get_preferencia_especie_animal_display(),
            'preferencia_porte_animal_display': p.get_preferencia_porte_animal_display(),
            'tipo_residencia_display': p.get_tipo_residencia_display(),
            'nivel_atividade_usuario_display': p.get_nivel_atividade_usuario_display(),
            'experiencia_animais_display': p.get_experiencia_animais_display(),
            'idades_criancas_display_list': p.get_idades_criancas_display_list(),
        })(perfil_usuario) 

    except Perfil.DoesNotExist:
        messages.warning(request, 'Para melhores recomendações, complete seu perfil! Exibindo todos os animais disponíveis.')
        animais_para_adocao_qs = await sync_to_async(Animal.objects.filter)(disponivel_adocao=True, ativo=True)
        animais_para_adocao = await sync_to_async(list)(animais_para_adocao_qs.order_by('nome'))
        context = {
            'animais': animais_para_adocao,
            'perfil_completo': False
        }
        return render(request, "muralpets.html", context)

    animais_disponiveis_qs = await sync_to_async(Animal.objects.filter)(disponivel_adocao=True, ativo=True)
    animais_disponiveis_list = await sync_to_async(list)(animais_disponiveis_qs)

    animais_com_pontuacao = []
    porte_order = {'pequeno': 1, 'medio': 2, 'grande': 3, 'gigante': 4, 'qualquer': 0}

    for animal in animais_disponiveis_list:
        pontuacao_gemini = 0
        explicacao_gemini = ""
        forced_zero = False 
        motivos_desqualificacao = [] 

        animal_data = await sync_to_async(lambda a: {
            'nome': a.nome,
            'socializacao_criancas_raw': a.socializacao_criancas,
            'socializacao_criancas_display': a.get_socializacao_criancas_display(),
            'necessidades_especiais': a.necessidades_especiais,
            'socializacao_outros_animais_raw': a.socializacao_outros_animais,
            'socializacao_outros_animais_display': a.get_socializacao_outros_animais_display(),
            'temperamento_raw': a.temperamento,
            'temperamento_display_list': a.get_temperamento_display_list(),
            'especie_raw': a.especie,
            'especie_display': a.get_especie_display(),
            'porte_raw': a.porte,
            'porte_display': a.get_porte_display(),
            'idade': a.idade,
            'nivel_energia_display': a.get_nivel_energia_display(),
            'descricao_necessidades': a.descricao_necessidades,
            'necessidade_espaco_display': a.get_necessidade_espaco_display(),
        })(animal) 

        if user_profile_data['tem_criancas'] and animal_data['socializacao_criancas_raw'] == 'nao':
            forced_zero = True
            motivos_desqualificacao.append(f"Animal '{animal_data['nome']}' não socializa com crianças e o perfil possui crianças.")
        
        if animal_data['necessidades_especiais'] and not user_profile_data['disposicao_necessidades_especiais']:
            forced_zero = True
            motivos_desqualificacao.append(f"Animal '{animal_data['nome']}' possui necessidades especiais e o perfil não está disposto a elas.")

        if user_profile_data['tem_outros_animais'] and animal_data['socializacao_outros_animais_raw'] == 'nao':
            forced_zero = True
            motivos_desqualificacao.append(f"Animal '{animal_data['nome']}' não socializa com outros animais e o perfil possui outros pets.")
            
        user_temperamento_outros_animais_list = user_profile_data['temperamento_outros_animais_raw']
        if user_profile_data['tem_outros_animais'] and user_temperamento_outros_animais_list:
            if any(kw in user_temperamento_outros_animais_list for kw in ['dominante', 'competitivo', 'agressivo', 'brigão']):
                animal_temperamento_lower = animal_data['temperamento_raw'].lower()
                if any(kw in animal_temperamento_lower for kw in ['timido', 'medroso', 'reservado', 'ansioso', 'nao_avaliado', 'desconhecido']):
                    forced_zero = True
                    motivos_desqualificacao.append(f"O temperamento dos outros animais do usuário pode ser um risco para o temperamento do animal '{animal_data['nome']}'.")

        temperamento_lower = animal_data['temperamento_raw'].lower()
        temperamento_keywords_criticas = [
            'agressivo', 'reage mal', 'morde', 'não se dá', 'brigão', 'violento', 'confusento',
            'hostil', 'perigoso', 'ataca', 'rosna', 'arredio', 'difícil', 'intolerante'
        ]
        if any(keyword in temperamento_lower for keyword in temperamento_keywords_criticas):
            forced_zero = True
            motivos_desqualificacao.append(f"Animal '{animal_data['nome']}' possui temperamento problemático/agressivo: '{animal_data['temperamento_raw']}'.")
        
        if user_profile_data['preferencia_especie_animal'] != 'qualquer' and \
           user_profile_data['preferencia_especie_animal'] != animal_data['especie_raw']:
            forced_zero = True
            motivos_desqualificacao.append(f"Animal '{animal_data['nome']}' não corresponde à espécie preferida do usuário ('{user_profile_data['preferencia_especie_animal_display']}').")

        user_pref_porte_rank = porte_order.get(user_profile_data['preferencia_porte_animal'], 0)
        animal_porte_rank = porte_order.get(animal_data['porte_raw'], 0)

        if user_profile_data['preferencia_porte_animal'] != 'qualquer' and \
           abs(user_pref_porte_rank - animal_porte_rank) >= 2:
            forced_zero = True
            motivos_desqualificacao.append(f"Animal '{animal_data['nome']}' possui porte muito diferente do preferencial: {user_profile_data['preferencia_porte_animal_display']}.")

        if forced_zero:
            pontuacao_gemini = 0
            explicacao_gemini = "INCOMPATIBILIDADE CRÍTICA DETECTADA: " + " ".join(motivos_desqualificacao) + " Por favor, considere outro animal."
        else:
            pontuacao_gemini, explicacao_gemini = await get_gemini_compatibility_score(perfil_usuario, animal)
        
        animal.gemini_pontuacao = pontuacao_gemini
        animal.gemini_explicacao = explicacao_gemini
        
        if pontuacao_gemini > 0:
            animais_com_pontuacao.append((pontuacao_gemini, animal))

    animais_com_pontuacao.sort(key=lambda x: x[0], reverse=True)
    animais_ordenados = [animal for score, animal in animais_com_pontuacao]

    context = {
        'animais': animais_ordenados,
        'perfil_completo': True 
    }
    return render(request, "muralpets.html", context)


### Views de Chat e Perfil Público

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

@login_required
def detalhes_animal(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id)
    dono_perfil = animal.owner

    pode_iniciar_chat = (request.user != dono_perfil.user)

    context = {
        'animal': animal,
        'dono_perfil': dono_perfil,
        'pode_iniciar_chat': pode_iniciar_chat,
    }
    return render(request, 'detalhes_animal.html', context)

@login_required
def iniciar_chat(request, dono_perfil_id, animal_id):
    solicitante_perfil = get_object_or_404(Perfil, user=request.user)
    dono_perfil = get_object_or_404(Perfil, id=dono_perfil_id)
    animal = get_object_or_404(Animal, id=animal_id)

    if solicitante_perfil == dono_perfil:
        messages.error(request, "Você não pode iniciar um chat com seu próprio perfil ou sobre seu próprio pet.")
        return redirect('detalhes_animal', animal_id=animal.id)

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
            messages.success(request, 'Mensagem enviada com sucesso!')

            destinatario_perfil = conversa.solicitante if conversa.dono == request.user.perfil else conversa.dono
            assunto_notificacao = f"Nova resposta na conversa sobre {conversa.animal.nome} - MyPet"
            corpo_notificacao = f"""
            Olá, {destinatario_perfil.user.first_name if destinatario_perfil.user.first_name else destinatario_perfil.user.username},

            Você recebeu uma nova mensagem de {solicitante_perfil.user.first_name if solicitante_perfil.user.first_name else solicitante_perfil.user.username}
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
                mensagens = conversa.mensagens.all()
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

            destinatario_perfil = conversa.solicitante if conversa.dono == request.user.perfil else conversa.dono
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
            mensagens = conversa.mensagens.all()
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