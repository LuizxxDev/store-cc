# config.py
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Token do Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

MERCADOPAGO_ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")

# Usuários permitidos (IDs de admin)
ALLOWED_USERS = list(map(int, os.getenv("ALLOWED_USERS", "").split(",")))
