import asyncio
from aiogram import F, Dispatcher, Bot
from aiogram.types import Message
from handlers import comstart, oplata, price_handler
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import config
import httpx
from database import init_db, get_session
from models import notify_users
from aiogram.types import CallbackQuery
from fastapi import FastAPI, HTTPException
bot = Bot(config.TOKEN_BOT)
dp = Dispatcher()

app = FastAPI()
from huobi_client import HuobiClient

# Конфигурация
API_KEY = "98dedb3c-778aeafb-64ff43f2-rfhfg2mkl3"
SECRET_KEY = "ff87d909-64596f36-872e6ca1-77930"

huobi_client = HuobiClient(api_key=API_KEY, secret_key=SECRET_KEY)

async def get_deposit_addresses(session: AsyncSession, user_id: int, currencies: list):

    # Получаем `sub_uid` пользователя
    result = await session.execute(
        select(User.sub_uid).where(User.id == user_id)
    )
    sub_uid = result.scalar_one_or_none()

    if not sub_uid:
        raise ValueError(f"Sub-Account не найден для пользователя {user_id}")

    # Получаем адреса для всех указанных валют
    addresses = []
    for currency in currencies:
        response = await huobi_client.get_deposit_address(sub_uid=sub_uid, currency=currency)
        address_data = response["data"]
        
        # Сохраняем адрес в таблицу `wallets`
        wallet = Wallet(
            user_id=user_id,
            currency=currency,
            wallet_address=address_data["address"],
            chain=address_data["chain"]
        )
        session.add(wallet)
        addresses.append(address_data)

    await session.commit()
    return addresses


# Функция получения адресов для валюты
async def fetch_payment_address(currency: str, sub_id:int):
    try:
        response = await huobi_client.get_sub_deposit_address(currency,sub_id)
        print(f"Response from Huobi: {response}")  # Логируем полный ответ

        if response.get("code") == 1002:
            print("Error: Unauthorized access.")  # Логируем ошибку
            raise ValueError("Unauthorized access. Please check your API key and permissions.")

        if response.get("code") != 200:
            print("Error: Failed to fetch deposit address.")  # Логируем ошибку
            raise ValueError("Failed to fetch deposit address.")

        # Формируем список адресов
        address_data = [
            {"address": entry.get("address"), "chain": entry.get("chain")}
            for entry in response.get("data", [])
        ]

        if not address_data:
            print("No deposit addresses found.")  # Логируем пустой ответ
            raise ValueError("No deposit addresses found for the specified currency.")

        print(f"Processed addresses: {address_data}")  # Логируем обработанные адреса
        return address_data

    except Exception as e:
        print(f"Error during address fetch: {str(e)}")  # Логируем исключение
        raise



async def check_payment_history(currency: str):
    # Получаем историю депозитов для конкретной валюты
    deposit_history = await huobi_client.get_deposit_history(currency="usdt")
    print(deposit_history)
    print("123")
    
    if deposit_history.get("code") == 200 and "data" in deposit_history:
        for entry in deposit_history["data"]:
            # Извлекаем информацию о каждой транзакции
            address = entry.get("address")
            amount = entry.get("amount")
            status = entry.get("status")
            print(f"Адрес: {address}, Сумма: {amount}, Статус: {status}")
            
            # Дополнительная проверка на статус или другие условия
            if status == "success":
                print(f"Пополнение успешно на адрес {address}")
                return True
    return False

# API-эндпоинт для получения адресов
@app.get("/get-payment-address/{currency}")
async def get_payment_address(currency: str):
    try:
        # Вызываем автономную функцию для получения данных
        address_data = await fetch_payment_address(currency)
        return {"status": "success", "addresses": address_data}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "home page"}



async def get_sub_address(sub_uid: int, currency: str):
    response = await huobi_client.get_sub_deposit_address(currency=currency, sub_uid=sub_uid)
    print("\n\n",response,"\n\n")
    
async def get_sub_accounts():
    response = await huobi_client.get_sub_users_list()
    print("\n\n",response,"\n\n")


async def periodic_check(bot: Bot):
    while True:
        async for session in get_session():
            await notify_users(session, bot, days_before_end=config.DAYS_BEFOR)

        await asyncio.sleep(24 * 60 * 60)


@dp.callback_query(F.data == ( 'fff'))
async def pay_sub_func(call: CallbackQuery, bot: Bot):
    async for session in get_session():
        await notify_users(session=session,bot=bot,days_before_end=config.DAYS_BEFOR)
    
    await call.answer("попытались")
    

async def main():
    await init_db()
    print('Бд врубил')
    asyncio.create_task(periodic_check(bot))

    await bot.delete_webhook(drop_pending_updates=True)
    dp.include_routers(
        comstart.router,
        oplata.router,
        price_handler.router
    )
    await dp.start_polling(bot,skip_updates=True)
    
if __name__ == "__main__":
    asyncio.run(main())
    