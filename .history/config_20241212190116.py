from dotenv import load_dotenv
import os

load_dotenv()


TOKEN_BOT = os.getenv('TOKEN_BOT')
PUB_KEY = '98dedb3c-778aeafb-64ff43f2-rfhfg2mkl3'
SEC_KEY = 'ff87d909-64596f36-872e6ca1-77930'
API = os.getenv('API')
PRICE = float(os.getenv('PRICE', 0))
BNB_PRICE = float(os.getenv('BNB_PRICE', 0))
ADMINS = [int(admin.strip()) for admin in os.getenv('ADMINS', '').split(',') if admin.strip().isdigit()]
DAYS_BEFOR = int(os.getenv('DAYS_BEFOR', 0))