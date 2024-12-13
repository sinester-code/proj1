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
    """
    Запрашивает цену криптовалюты по символу через API CoinMarketCap.
    """
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

        # Получение цены монеты
        price = await fetch_crypto_price(symbol)

        # Расчет количества монет за указанную сумму
        quantity = amount_usd / price

        await message.answer(
            f"Текущая цена {symbol}: ${price:.2f}\n"
            f"На ${amount_usd} вы можете купить: {quantity:.6f} {symbol}"
        )

    except ValueError as e:
        await message.answer(f"Ошибка: {e}")
    except Exception as e:
        await message.answer("Не удалось получить данные. Проверьте символ и повторите попытку.")

if __name__ == "__main__":
    dp.run_polling(bot)