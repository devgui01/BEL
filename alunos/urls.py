from django.urls import path
from . import views

urlpatterns = [
    path('entrar/', views.role_select, name='role-select'),
    path('aluno/login/', views.aluno_login_placeholder, name='aluno-login'),
    path('', views.AlunoListView.as_view(), name='aluno-list'),
    path('novo/', views.AlunoCreateView.as_view(), name='aluno-create'),
    path('editar/<int:pk>/', views.AlunoUpdateView.as_view(), name='aluno-update'),
    path('mensalidades/', views.MensalidadeListView.as_view(), name='mensalidade-list'),
    path('mensalidades/registrar-pagamento/<int:pk>/', views.registrar_pagamento, name='registrar-pagamento'),
    path('mensalidades/gerar/', views.gerar_mensalidades, name='gerar-mensalidades'),
    path('mensalidades/excluir/<int:pk>/', views.excluir_mensalidade, name='excluir-mensalidade'),
    path('mensalidades/editar-mensalidade/<int:pk>/', views.editar_mensalidade, name='editar-mensalidade'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('update-theme/', views.update_theme, name='update-theme'),
    path('relatorios/mensal/', views.relatorio_mensal, name='relatorio-mensal'),
    path('presencas/', views.presencas_view, name='presencas'),
] 