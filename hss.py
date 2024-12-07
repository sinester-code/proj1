from fastapi import FastAPI, HTTPException
from huobi_client import HuobiClient

app = FastAPI()

# Конфигурация
API_KEY = "b1rkuf4drg-c73d0613-19797138-a8d2c"
SECRET_KEY = "1d9262a2-5f14b6cc-e1541743-75404"

huobi_client = HuobiClient(api_key=API_KEY, secret_key=SECRET_KEY)

# Функция получения адресов для валюты
async def fetch_payment_address(currency: str):
    try:
        response = await huobi_client.get_deposit_address(currency)
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
