# 🚀 Instruções para Deploy no Render

## 📋 Pré-requisitos
- Conta no Render.com (já criada)
- Projeto no GitHub (opcional, mas recomendado)

## 🔧 Passos para Deploy

### 1. Preparar o Projeto
- ✅ Arquivo `build.sh` criado
- ✅ Arquivo `render.yaml` criado  
- ✅ `requirements.txt` atualizado
- ✅ Configurações do Django já preparadas para produção

### 2. No Dashboard do Render

#### 2.1 Criar o Banco de Dados PostgreSQL
1. Clique em **"New"** → **"PostgreSQL"**
2. Nome: `ctgouveia-db`
3. Plano: **Free**
4. Clique em **"Create Database"**
5. **IMPORTANTE**: Anote as credenciais do banco (serão mostradas apenas uma vez!)

#### 2.2 Criar o Serviço Web
1. Clique em **"New"** → **"Web Service"**
2. Conecte seu repositório GitHub (ou faça upload manual)
3. Nome: `ctgouveia`
4. Runtime: **Python 3**
5. Build Command: `./build.sh`
6. Start Command: `gunicorn ct_gouveia.wsgi:application`

#### 2.3 Configurar Variáveis de Ambiente
No serviço web, adicione estas variáveis:

| Chave | Valor |
|-------|-------|
| `SECRET_KEY` | Gere uma chave aleatória (ou deixe o Render gerar) |
| `DATABASE_URL` | URL do banco PostgreSQL criado |
| `RENDER` | `true` |
| `DEBUG` | `false` |

### 3. Configurações Importantes

#### 3.1 Banco de Dados
- O Django já está configurado para usar PostgreSQL em produção
- As migrações rodarão automaticamente durante o build

#### 3.2 Arquivos Estáticos
- O WhiteNoise já está configurado para servir arquivos estáticos
- Os arquivos serão coletados automaticamente durante o build

#### 3.3 Segurança
- `DEBUG=False` em produção
- `SECRET_KEY` será gerada automaticamente pelo Render
- `ALLOWED_HOSTS` já configurado para o domínio do Render

## 🌐 Após o Deploy

1. Acesse: `https://ctgouveia.onrender.com`
2. Crie um superusuário para acessar o admin:
   ```bash
   python manage.py createsuperuser
   ```
3. Acesse `/admin/` para gerenciar o sistema

## 🔍 Troubleshooting

### Erro de Build
- Verifique se o `build.sh` tem permissão de execução
- Confirme se todas as dependências estão no `requirements.txt`

### Erro de Banco
- Verifique se a `DATABASE_URL` está correta
- Confirme se o banco PostgreSQL está ativo

### Erro de Arquivos Estáticos
- Verifique se o WhiteNoise está no `MIDDLEWARE`
- Confirme se `STATIC_ROOT` está configurado

## 📱 Funcionalidades do Sistema

- **Login/Logout**: `/accounts/login/`
- **Admin**: `/admin/`
- **Alunos**: `/alunos/`
- **Gestão de Mensalidades**: Sistema completo de pagamentos
- **Relatórios**: Controle de alunos e financeiro

## 🎯 Próximos Passos

1. Fazer commit das alterações no Git
2. Conectar o repositório ao Render
3. Configurar as variáveis de ambiente
4. Fazer o primeiro deploy
5. Testar todas as funcionalidades
6. Configurar domínio personalizado (opcional)
