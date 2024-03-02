#!/bin/bash

# Comando para criar um ambiente virtual Python
python3 -m venv .venv

# Comando para ativar o ambiente virtual
source .venv/bin/activate

# Comando para instalar as dependências do Python a partir do arquivo requirements.txt
pip install -r requirements.txt