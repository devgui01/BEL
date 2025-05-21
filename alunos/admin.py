from django.contrib import admin
from .models import Aluno, Mensalidade

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'faixa', 'telefone', 'ativo', 'bolsista')
    list_filter = ('faixa', 'ativo', 'bolsista')
    search_fields = ('nome', 'telefone', 'email')

@admin.register(Mensalidade)
class MensalidadeAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'data_vencimento', 'valor', 'status', 'data_pagamento')
    list_filter = ('status', 'data_vencimento')
    search_fields = ('aluno__nome',)
