from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Aluno, Mensalidade, Pagamento
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, OuterRef, Subquery, Max, Case, When, Value, F, CharField
from .forms import GerarMensalidadeForm, AlunoForm, SignUpForm, ProfileForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
import calendar
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required

# Create your views here.

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

class AlunoCreateView(LoginRequiredMixin, CreateView):
    model = Aluno
    template_name = 'alunos/aluno_form.html'
    form_class = AlunoForm
    success_url = reverse_lazy('aluno-list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Aluno cadastrado com sucesso!')
        return super().form_valid(form)

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
        
        # Processar mensalidades para obter a mais recente por aluno
        mensalidades_por_aluno = {}
        for mensalidade in context['mensalidades']:
            # Usa a ordenação para garantir que a primeira encontrada para um aluno seja a mais recente
            if mensalidade.aluno not in mensalidades_por_aluno:
                # Determinar o status para exibição (incluindo atrasado)
                status_exibicao = mensalidade.status
                if status_exibicao == 'PENDENTE' and mensalidade.data_vencimento < timezone.now().date():
                     status_exibicao = 'ATRASADO'
                
                # Adicionar a mensalidade mais recente e seu status de exibição
                mensalidades_por_aluno[mensalidade.aluno] = {
                    'mensalidade': mensalidade,
                    'status_exibicao': status_exibicao
                }

        # Passar apenas as mensalidades mais recentes para o template
        # Converter de volta para uma lista de objetos Mensalidade (ou dicionários)
        context['mensalidades'] = [item['mensalidade'] for item in mensalidades_por_aluno.values()]
        # Passar também o status de exibição associado
        context['mensalidades_com_status'] = mensalidades_por_aluno.values()

        # Manter search query se necessário, embora não esteja na lista de mensalidades por aluno
        # context['search_query'] = self.request.GET.get('search', '') # Remover se não for usar busca aqui

        return context

@login_required
def registrar_pagamento(request, pk):
    if request.method == 'POST':
        try:
            mensalidade = get_object_or_404(Mensalidade, pk=pk, aluno__owner=request.user)
            if mensalidade.status != 'PAGO':
                # Atualiza o status da mensalidade
                mensalidade.status = 'PAGO'
                mensalidade.data_pagamento = timezone.now()
                mensalidade.save()
                
                # Criar próxima mensalidade com vencimento um mês após a data do pagamento
                data_pagamento_atual = mensalidade.data_pagamento
                proxima_data = (data_pagamento_atual.replace(day=1) + timedelta(days=32)).replace(day=data_pagamento_atual.day)
                
                # Ajuste para meses com menos dias que o dia do pagamento
                last_day_of_next_month = calendar.monthrange(proxima_data.year, proxima_data.month)[1]
                if proxima_data.day > last_day_of_next_month:
                    proxima_data = proxima_data.replace(day=last_day_of_next_month)

                Mensalidade.objects.create(
                    aluno=mensalidade.aluno,
                    data_vencimento=proxima_data,
                    valor=100.00 if mensalidade.aluno.bolsista else 150.00,
                    status='PENDENTE'
                )
                
                messages.success(request, 'Pagamento registrado com sucesso! Nova mensalidade gerada.')
                return redirect('mensalidade-list')
            else:
                messages.warning(request, 'Esta mensalidade já foi paga.')
                return redirect('mensalidade-list')
        except Exception as e:
            messages.error(request, f'Erro ao registrar pagamento: {str(e)}')
            return redirect('mensalidade-list')
    return redirect('mensalidade-list')

@login_required
def gerar_mensalidades(request):
    if request.method == 'POST':
        alunos_ativos = Aluno.objects.filter(ativo=True, owner=request.user)
        hoje = timezone.now().date()
        # A data de vencimento para a nova mensalidade será o primeiro dia do próximo mês a partir de hoje
        primeiro_dia_proximo_mes = (hoje.replace(day=1) + timedelta(days=32)).replace(day=1)

        mensalidades_geradas_count = 0
        for aluno in alunos_ativos:
            # Verifica se já existe uma mensalidade PENDENTE para este aluno (não apenas para o próximo mês)
            mensalidade_pendente_existente = Mensalidade.objects.filter(
                aluno=aluno,
                status='PENDENTE'
            ).exists()

            if not mensalidade_pendente_existente:
                Mensalidade.objects.create(
                    aluno=aluno,
                    data_vencimento=primeiro_dia_proximo_mes, # Nova mensalidade vence no início do próximo mês
                    valor=100.00 if aluno.bolsista else 150.00,
                    status='PENDENTE'
                )
                mensalidades_geradas_count += 1
            # else:
                # Poderíamos adicionar uma mensagem aqui por aluno, mas pode gerar muitas mensagens.
                # messages.info(request, f'Aluno {aluno.nome} já possui mensalidade pendente.')

        if mensalidades_geradas_count > 0:
             messages.success(request, f'{mensalidades_geradas_count} mensalidade(s) gerada(s) com sucesso para alunos ativos sem pendências!')
        else:
             messages.info(request, 'Nenhuma mensalidade nova gerada. Todos os alunos ativos já possuem mensalidade pendente.')

        return redirect('mensalidade-list')

    else:
        # Se for um GET request, apenas exibe o template do botão ou formulário se houver
        form = GerarMensalidadeForm(user=request.user)
        return render(request, 'alunos/gerar_mensalidade.html', { 'form': form }) 

@login_required
def excluir_mensalidade(request, pk):
    if request.method == 'POST':
        try:
            mensalidade = Mensalidade.objects.get(id=pk, aluno__owner=request.user)
            mensalidade.delete()
            messages.success(request, 'Mensalidade excluída com sucesso!')
        except Mensalidade.DoesNotExist:
            messages.error(request, 'Mensalidade não encontrada.')
        except Exception as e:
            messages.error(request, f'Erro ao excluir mensalidade: {e}')
    return redirect('mensalidade-list')

@login_required
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

@login_required
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

@login_required
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

@login_required
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