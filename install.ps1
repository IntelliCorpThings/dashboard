# Script PowerShell

# Comando para criar um ambiente virtual Python
python -m venv .venv

# Comando para ativar o ambiente virtual (usando o script Activate.ps1)
. .\.venv\Scripts\Activate.ps1

# Comando para instalar as dependências do Python a partir do arquivo requirements.txt
pip install -r .\requirements.txt