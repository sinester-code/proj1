import os
from decimal import Decimal
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv
import httpx
from config import API, PRICE

router = Router()

API_KEY = API
BASE_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"


async def fetch_crypto_price(symbol: str) -> Decimal:
    headers = {"X-CMC_PRO_API_KEY": API_KEY}
    params = {"symbol": symbol, "convert": "USD"}

    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL, headers=headers, params=params)
        data = response.json()

        if response.status_code != 200:
            raise ValueError(f"Ошибка API: {data.get('status', {}).get('error_message', 'Неизвестная ошибка')}")

        # Получение цены
        price = Decimal(data["data"][symbol]["quote"]["USD"]["price"])
        return price

async def get_price(symbol:str):
    try:
        amount_usd = PRICE

        price = await fetch_crypto_price(symbol)

        kol_vo = amount_usd / price

        print(
            f"Текущая цена {symbol}: ${price:.2f}\n"
            f"На ${amount_usd} вы можете купить: {kol_vo:.6f} {symbol}"
        )

    except ValueError as e:
        await message.answer(f"{e}")
    except Exception as e:
        pass
