from dotenv import load_dotenv
import os

load_dotenv()


TOKEN_BOT = os.getenv('TOKEN_BOT')
PUB_KEY = os.getenv('PUB_KEY')
SEC_KEY = os.getenv('SEC_KEY')
API = os.getenv('API')
PRICE = float(os.getenv('PRICE', 0))
BNB_PRICE = float(os.getenv('BNB_PRICE', 0))
ADMINS = [int(admin.strip()) for admin in os.getenv('ADMINS', '').split(',') if admin.strip().isdigit()]
DAYS_BEFOR = int(os.getenv('DAYS_BEFOR', 0))