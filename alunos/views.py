from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Aluno, Mensalidade, Pagamento
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, OuterRef, Subquery, Max, Case, When, Value, F, CharField, Count
from django.db import transaction
from .forms import GerarMensalidadeForm, AlunoForm, SignUpForm, ProfileForm, PresencaForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
import calendar
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.utils import timezone as dj_tz

# Create your views here.

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test

def is_professor(user):
    return user.is_authenticated and user.is_staff

def professor_required(view_func):
    return login_required(user_passes_test(is_professor, login_url='role-select')(view_func))


@method_decorator(user_passes_test(is_professor, login_url='role-select'), name='dispatch')
class AlunoListView(LoginRequiredMixin, ListView):
    model = Aluno
    template_name = 'alunos/aluno_list.html'
    context_object_name = 'alunos'

    def get_queryset(self):
        queryset = super().get_queryset().filter(owner=self.request.user)
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(nome__icontains=search_query) |
                Q(telefone__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context

@method_decorator(user_passes_test(is_professor, login_url='role-select'), name='dispatch')
class AlunoCreateView(LoginRequiredMixin, CreateView):
    model = Aluno
    template_name = 'alunos/aluno_form.html'
    form_class = AlunoForm
    success_url = reverse_lazy('aluno-list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Aluno cadastrado com sucesso!')
        return super().form_valid(form)

@method_decorator(user_passes_test(is_professor, login_url='role-select'), name='dispatch')
class AlunoUpdateView(LoginRequiredMixin, UpdateView):
    model = Aluno
    template_name = 'alunos/aluno_form.html'
    form_class = AlunoForm
    success_url = reverse_lazy('aluno-list')

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Dados do aluno atualizados com sucesso!')
        return super().form_valid(form)

@method_decorator(user_passes_test(is_professor, login_url='role-select'), name='dispatch')
class MensalidadeListView(LoginRequiredMixin, ListView):
    model = Mensalidade
    template_name = 'alunos/mensalidade_list.html'
    context_object_name = 'mensalidades'

    def get_queryset(self):
        # Buscar todas as mensalidades ativas (não excluídas)
        # Como não temos um campo de exclusão lógica, buscar todas e filtrar no context
        return Mensalidade.objects.filter(aluno__owner=self.request.user).order_by('aluno', '-data_vencimento') # Ordena por aluno e data decrescente

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = timezone.localdate()
        mensalidades_por_aluno = {}
        ultima_por_aluno = {}
        for m in context['mensalidades']:
            ultima_por_aluno[m.aluno] = m
            if m.data_vencimento <= hoje and m.aluno not in mensalidades_por_aluno:
                status_exibicao = m.status
                if status_exibicao == 'PENDENTE' and m.data_vencimento < hoje:
                    status_exibicao = 'ATRASADO'
                mensalidades_por_aluno[m.aluno] = {
                    'mensalidade': m,
                    'status_exibicao': status_exibicao
                }

        for aluno, m in ultima_por_aluno.items():
            if aluno not in mensalidades_por_aluno:
                mensalidades_por_aluno[aluno] = {
                    'mensalidade': m,
                    'status_exibicao': m.status
                }

        context['mensalidades'] = [item['mensalidade'] for item in mensalidades_por_aluno.values()]
        context['mensalidades_com_status'] = mensalidades_por_aluno.values()
        return context

@professor_required
def registrar_pagamento(request, pk):
    if request.method == 'POST':
        try:
            mensalidade = get_object_or_404(Mensalidade, pk=pk, aluno__owner=request.user)
            if mensalidade.status != 'PAGO':
                with transaction.atomic():
                    mensalidade.status = 'PAGO'
                    mensalidade.data_pagamento = timezone.localdate()
                    mensalidade.save()

                messages.success(request, 'Pagamento registrado com sucesso!')
                return redirect('mensalidade-list')
            else:
                messages.warning(request, 'Esta mensalidade já foi paga.')
                return redirect('mensalidade-list')
        except Exception as e:
            messages.error(request, f'Erro ao registrar pagamento: {str(e)}')
            return redirect('mensalidade-list')
    return redirect('mensalidade-list')

@professor_required
def gerar_mensalidades(request):
    if request.method == 'POST':
        # POST do formulário manual
        if 'aluno' in request.POST:
            form = GerarMensalidadeForm(request.POST, user=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Mensalidade criada com sucesso!')
                return redirect('mensalidade-list')
            else:
                return render(request, 'alunos/gerar_mensalidade.html', {'form': form})

        # Geração em massa
        alunos_ativos = Aluno.objects.filter(ativo=True, owner=request.user)
        hoje = timezone.localdate()
        primeiro_dia_proximo_mes = (hoje.replace(day=1) + timedelta(days=32)).replace(day=1)

        mensalidades_geradas_count = 0
        for aluno in alunos_ativos:
            mensalidade_pendente_existente = Mensalidade.objects.filter(
                aluno=aluno,
                status='PENDENTE'
            ).exists()

            if not mensalidade_pendente_existente:
                Mensalidade.objects.create(
                    aluno=aluno,
                    data_vencimento=primeiro_dia_proximo_mes,
                    valor=100.00 if aluno.bolsista else 150.00,
                    status='PENDENTE'
                )
                mensalidades_geradas_count += 1

        if mensalidades_geradas_count > 0:
            messages.success(request, f'{mensalidades_geradas_count} mensalidade(s) gerada(s) com sucesso para alunos ativos sem pendências!')
        else:
            messages.info(request, 'Nenhuma mensalidade nova gerada. Todos os alunos ativos já possuem mensalidade pendente.')

        return redirect('mensalidade-list')

    else:
        # Se for um GET request, apenas exibe o template do botão ou formulário se houver
        form = GerarMensalidadeForm(user=request.user)
        return render(request, 'alunos/gerar_mensalidade.html', { 'form': form }) 

@professor_required
def excluir_mensalidade(request, pk):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                mensalidade = get_object_or_404(Mensalidade, id=pk, aluno__owner=request.user)
                mensalidade.delete()
            messages.success(request, 'Mensalidade excluída com sucesso!')
        except Mensalidade.DoesNotExist:
            messages.error(request, 'Mensalidade não encontrada.')
        except Exception as e:
            messages.error(request, f'Erro ao excluir mensalidade: {e}')
    return redirect('mensalidade-list')

@professor_required
def editar_mensalidade(request, pk):
    mensalidade = get_object_or_404(Mensalidade, pk=pk, aluno__owner=request.user)
    if request.method == 'POST':
        form = GerarMensalidadeForm(request.POST, instance=mensalidade, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mensalidade alterada com sucesso!')
            return redirect('mensalidade-list')
    else:
        form = GerarMensalidadeForm(instance=mensalidade, user=request.user)
    return render(request, 'alunos/gerar_mensalidade.html', {'form': form, 'editar': True})

# View para registro de novos usuários do sistema
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Conta criada com sucesso! Faça login para continuar.')
            return redirect('login') # Redireciona para a página de login (URL name 'login')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

@professor_required
def settings_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configurações atualizadas com sucesso!')
            return redirect('settings')
    else:
        form = ProfileForm(instance=request.user.profile)
    
    return render(request, 'alunos/settings.html', {'form': form})

@professor_required
def update_theme(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            dark_mode = data.get('dark_mode', False)
            request.user.profile.dark_mode = dark_mode
            request.user.profile.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@professor_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user.profile)
    
    return render(request, 'alunos/profile.html', {'form': form})

def role_select(request):
    """Tela inicial: escolha entre Professor (sistema atual) e Aluno (portal do aluno)."""
    return render(request, 'alunos/role_select.html')

def aluno_login_placeholder(request):
    """Login do aluno. Autentica usuário e redireciona para o portal do aluno."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('aluno-portal')
    else:
        form = AuthenticationForm(request)
    return render(request, 'alunos/portal_aluno_login.html', { 'form': form })

@login_required
def aluno_portal_home(request):
    """Home simples do portal do aluno (acesso autenticado)."""
    profile = request.user.profile
    if not profile.accepted_terms_at:
        return redirect('aluno-termos')
    return render(request, 'alunos/portal_aluno_home.html')

def aluno_signup(request):
    """Cadastro de conta para alunos. Cria usuário padrão (não staff) e faz login."""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Garante perfil criado pelo sinal e que não é staff
            user.is_staff = False
            user.save()
            auth_login(request, user)
            messages.success(request, 'Conta de aluno criada com sucesso!')
            return redirect('aluno-portal')
    else:
        form = SignUpForm()
    return render(request, 'alunos/portal_aluno_signup.html', { 'form': form })

@login_required
def aluno_termos(request):
    TERMS_VERSION = '2025-08-20'
    if request.method == 'POST':
        aceitar = request.POST.get('aceitar') == 'on'
        if aceitar:
            p = request.user.profile
            p.accepted_terms_at = dj_tz.now()
            p.accepted_terms_version = TERMS_VERSION
            p.save()
            messages.success(request, 'Termo aceito. Bem-vindo!')
            return redirect('aluno-portal')
        else:
            messages.error(request, 'Você precisa aceitar o termo para continuar.')
    return render(request, 'alunos/portal_aluno_termos.html', { 'version': TERMS_VERSION })

@login_required
def relatorio_mensal(request):
    """Relatório A4 imprimível de receitas do mês por mensalidades pagas."""
    # Determina mês/ano selecionados (padrão: mês atual em timezone local)
    hoje = timezone.localdate()
    try:
        mes = int(request.GET.get('mes', hoje.month))
        ano = int(request.GET.get('ano', hoje.year))
    except ValueError:
        mes, ano = hoje.month, hoje.year

    # Início e fim do mês
    inicio = hoje.replace(year=ano, month=mes, day=1)
    # calcula último dia do mês
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    fim = hoje.replace(year=ano, month=mes, day=ultimo_dia)

    # Filtra mensalidades pagas do usuário no período
    mensalidades_pagas = (
        Mensalidade.objects
        .filter(
            aluno__owner=request.user,
            status='PAGO',
            data_pagamento__isnull=False,
            data_pagamento__gte=inicio,
            data_pagamento__lte=fim,
        )
        .select_related('aluno')
        .order_by('data_pagamento')
    )

    total_receita = sum((m.valor for m in mensalidades_pagas), Decimal('0'))
    quantidade = mensalidades_pagas.count()

    # Série por dia para o gráfico (construída no servidor para evitar problemas de locale/parse)
    ultimo_dia = ultimo_dia = calendar.monthrange(ano, mes)[1]
    chart_labels = list(range(1, ultimo_dia + 1))
    chart_values = [0 for _ in chart_labels]
    for m in mensalidades_pagas:
        if m.data_pagamento:
            chart_values[m.data_pagamento.day - 1] += float(m.valor)

    meses_pt = [
        '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    meses = [{ 'num': i, 'nome': meses_pt[i] } for i in range(1, 12+1)]
    anos = list(range(hoje.year - 5, hoje.year + 1))

    context = {
        'mes': mes,
        'ano': ano,
        'inicio': inicio,
        'fim': fim,
        'mensalidades_pagas': mensalidades_pagas,
        'total_receita': total_receita,
        'quantidade': quantidade,
        'meses': meses,
        'anos': anos,
        'chart_labels': chart_labels,
        'chart_values': chart_values,
    }
    return render(request, 'alunos/relatorio.html', context)

@login_required
def presencas_view(request):
    """Página simples para registrar presenças por dia e ver lista recente."""
    if request.method == 'POST':
        form = PresencaForm(request.POST)
        if form.is_valid():
            # restringe alunos ao owner logado
            aluno = form.cleaned_data['aluno']
            if aluno.owner != request.user:
                messages.error(request, 'Aluno inválido.')
            else:
                form.save()
                messages.success(request, 'Presença registrada!')
                return redirect('presencas')
    else:
        form = PresencaForm()
        form.fields['aluno'].queryset = Aluno.objects.filter(owner=request.user, ativo=True).order_by('nome')

    # últimas 30 presenças do usuário
    from .models import Presenca
    presencas = Presenca.objects.filter(aluno__owner=request.user).select_related('aluno').order_by('-data', 'aluno__nome')[:30]

    # Ranking do mês atual (mais frequentes)
    hoje = timezone.localdate()
    inicio = hoje.replace(day=1)
    fim_dia = calendar.monthrange(hoje.year, hoje.month)[1]
    fim = hoje.replace(day=fim_dia)
    ranking_qs = (
        Presenca.objects
        .filter(aluno__owner=request.user, presente=True, data__gte=inicio, data__lte=fim)
        .values('aluno__nome')
        .annotate(total=Count('id'))
        .order_by('-total')[:10]
    )
    rank_labels = [r['aluno__nome'] for r in ranking_qs]
    rank_values = [r['total'] for r in ranking_qs]

    return render(request, 'alunos/presencas.html', { 'form': form, 'presencas': presencas, 'rank_labels': rank_labels, 'rank_values': rank_values })