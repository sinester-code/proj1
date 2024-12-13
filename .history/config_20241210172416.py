from dotenv import load_dotenv
import os

# Загрузка переменных окружения из .env
load_dotenv()

# Получение данных из .env
TOKEN_BOT = os.getenv('TOKEN_BOT')
PRICE = float(os.getenv('PRICE', 0))  # значение по умолчанию — 0
BNB_PRICE = float(os.getenv('BNB_PRICE', 0))
ADMINS = [int(admin.strip()) for admin in os.getenv('ADMINS', '').split(',') if admin.strip().isdigit()]
DAYS_BEFOR = int(os.getenv('DAYS_BEFOR', 0))

# Проверка, все ли значения загружены (опционально)
if not TOKEN_BOT:
    raise ValueError("TOKEN_BOT не задан в .env!")
