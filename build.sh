#!/usr/bin/env bash
# exit on error
set -o errexit

# Atualizar pip primeiro
pip install --upgrade pip

# Instalar dependências
pip install -r requirements.txt

# Coletar arquivos estáticos
python manage.py collectstatic --no-input

# Aplicar migrações
python manage.py migrate
