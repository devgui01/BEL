from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Aluno, Mensalidade, Pagamento
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from .forms import GerarMensalidadeForm

# Create your views here.

class AlunoListView(ListView):
    model = Aluno
    template_name = 'alunos/aluno_list.html'
    context_object_name = 'alunos'

    def get_queryset(self):
        queryset = super().get_queryset()
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

class AlunoCreateView(CreateView):
    model = Aluno
    template_name = 'alunos/aluno_form.html'
    fields = ['nome', 'data_nascimento', 'telefone', 'email', 'endereco', 'faixa', 'bolsista']
    success_url = reverse_lazy('aluno-list')

    def form_valid(self, form):
        messages.success(self.request, 'Aluno cadastrado com sucesso!')
        return super().form_valid(form)

class AlunoUpdateView(UpdateView):
    model = Aluno
    template_name = 'alunos/aluno_form.html'
    fields = ['nome', 'data_nascimento', 'telefone', 'email', 'endereco', 'faixa', 'bolsista', 'ativo']
    success_url = reverse_lazy('aluno-list')

    def form_valid(self, form):
        messages.success(self.request, 'Dados do aluno atualizados com sucesso!')
        return super().form_valid(form)

class MensalidadeListView(ListView):
    model = Mensalidade
    template_name = 'alunos/mensalidade_list.html'
    context_object_name = 'mensalidades'

    def get_queryset(self):
        # Mostra apenas mensalidades pendentes, ordenadas por data de vencimento
        return Mensalidade.objects.filter(pago=False).order_by('data_vencimento')

def registrar_pagamento(request, pk):
    mensalidade = get_object_or_404(Mensalidade, pk=pk)
    if not mensalidade.pago:
        # Atualiza o status da mensalidade
        mensalidade.pago = True
        mensalidade.data_pagamento = timezone.now()
        mensalidade.save()
        
        # Criar próxima mensalidade
        proxima_data = mensalidade.data_vencimento + timedelta(days=30)
        Mensalidade.objects.create(
            aluno=mensalidade.aluno,
            data_vencimento=proxima_data,
            valor=100.00 if mensalidade.aluno.bolsista else 150.00
        )
        
        messages.success(request, 'Pagamento registrado com sucesso! Nova mensalidade gerada.')
        return redirect('mensalidade-list')
    else:
        messages.warning(request, 'Esta mensalidade já foi paga.')
        return redirect('mensalidade-list')

def gerar_mensalidades(request):
    if request.method == 'POST':
        form = GerarMensalidadeForm(request.POST)
        if form.is_valid():
            mensalidade = form.save(commit=False)
            # Se o aluno for bolsista e o valor não foi alterado, usa o valor padrão
            if mensalidade.aluno.bolsista and mensalidade.valor == 150.00:
                mensalidade.valor = 100.00
            mensalidade.save()
            messages.success(request, 'Mensalidade gerada com sucesso!')
            return redirect('mensalidade-list')
    else:
        form = GerarMensalidadeForm()
        # Define a data de vencimento padrão para o próximo mês
        form.initial['data_vencimento'] = timezone.now().replace(day=1) + timedelta(days=32)
        form.initial['data_vencimento'] = form.initial['data_vencimento'].replace(day=1)
    
    return render(request, 'alunos/gerar_mensalidade.html', {'form': form})

def excluir_mensalidade(request, pk):
    mensalidade = Mensalidade.objects.get(id=pk)
    Pagamento.objects.filter(mensalidade=mensalidade).delete()
    mensalidade.delete()
    return redirect('mensalidade-list')

def editar_mensalidade(request, pk):
    mensalidade = get_object_or_404(Mensalidade, pk=pk)
    if request.method == 'POST':
        form = GerarMensalidadeForm(request.POST, instance=mensalidade)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mensalidade alterada com sucesso!')
            return redirect('mensalidade-list')
    else:
        form = GerarMensalidadeForm(instance=mensalidade)
    return render(request, 'alunos/gerar_mensalidade.html', {'form': form, 'editar': True})
