import time
import hmac
import hashlib
import base64
from urllib.parse import urlencode
import httpx
import json
from datetime import datetime
import config
from huobi.utils import LogInfo
class HuobiClient:
    def __init__(self, api_key: str, secret_key: str, base_url: str = "https://api.huobi.pro"):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url


    def _sign(self, method: str, endpoint: str, body: dict):
        # Текущее время
        timestamp = time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime())
        body.update({
            "AccessKeyId": self.api_key,
            "SignatureMethod": "HmacSHA256",
            "SignatureVersion": "2",
            "Timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        })

        # Формируем строку для подписи
        host = self.base_url.replace("https://", "")
        params = urlencode(sorted(body.items()))
        sign_str = f"{method}\n{host}\n{endpoint}\n{params}"

        # Генерация подписи
        signature = base64.b64encode(
            hmac.new(
                self.secret_key.encode("utf-8"),
                sign_str.encode("utf-8"),
                hashlib.sha256
            ).digest()
        )
        body["Signature"] = signature.decode("utf-8")
        return body
    async def get_sub_deposit_address(self, currency: str, sub_uid: str):
        """Получить адрес депозита для субаккаунта"""
        endpoint = "/v2/sub-user/deposit-address"
        
        # Параметры для запроса, включая идентификатор субаккаунта
        params = self._sign("GET", endpoint, {"currency": currency, "subUid": sub_uid})
        
        # Отладка параметров запроса
        print(f"Request params: {params}")
        
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(endpoint, params=params)
            
            if response.status_code == 200:
                response_data = response.json()  # Получаем JSON-данные
                print(f"Response: {response_data}")  # Печатаем ответ от сервера для отладки
                return response_data
            else:
                print(f"Error: {response.status_code}, {response.text}")
                return None
        
        
    async def create_sub_account(self, user_name: str, note: str = "Default Note"):
        """
        Создание sub-account на Huobi
        """
        endpoint = "/v2/sub-user/creation"
        url = f"{self.base_url}{endpoint}"
        
        # Тело запроса
        body = {
            "userList": [
                {"userName": user_name, "note": note}
            ]
        }
        
        # Подписываем запрос
        signed_params = self._sign("POST", endpoint, body)
        
        headers = {
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=signed_params, headers=headers)
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("code") == 200:
                    return response_data  # Успешный ответ
                else:
                    print(f"Ошибка: {response_data.get('message')}")
                    return None
            else:
                print(f"Ошибка HTTP: {response.status_code}, {response.text}")
                return None


    async def get_account_info(self):
        """Получить информацию об аккаунте"""
        endpoint = "/v1/account/accounts"
        params = self._sign("GET", endpoint, {})  # Вызов метода _sign с передачей метода и endpoint
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(endpoint, params=params)
            return response.json()

    async def get_deposit_address(self, currency: str):
        """Получить адрес депозита"""
        endpoint = "/v2/account/deposit/address"
        params = self._sign("GET", endpoint, {"currency": currency})  # Вызов метода _sign с передачей метода и endpoint
        print(f"Request params: {params}")  # Добавляем вывод параметров запроса для отладки
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(endpoint, params=params)
            response_data = response.json()  # Получаем JSON-данные
            print(f"Response: {response_data}")  # Печатаем ответ от сервера для отладки
            return response_data
        
        
    async def get_sub_users_list(self):
        """Получить список субаккаунтов без использования fromId"""
        endpoint = "/v2/sub-user/user-list"
        
        # Параметры запроса без fromId
        params = self._sign("GET", endpoint, {})
        
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(endpoint, params=params)
            
            # Проверка успешности ответа
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("code") == 200:
                    sub_users = response_data["data"]
                    
                    # Печать результатов для отладки
                    print(f"Sub Users: {sub_users}")
                    
                    return sub_users
                else:
                    print(f"Ошибка: {response_data.get('message')}")
                    return None
            else:
                print(f"Ошибка HTTP: {response.status_code}, {response.text}")
                return None

        
    async def get_sub_deposit_history(self, sub_uid: str, currency: str = None, limit: int = 100):
        """
        Запрос истории депозитов субаккаунта.
        :param sub_uid: UID субаккаунта.
        :param currency: Валюта (например, "usdt"). Если None, возвращаются все валюты.
        :param limit: Максимальное количество записей (1-500).
        """
        endpoint = "/v2/sub-user/query-deposit"
        params = {
            "subUid": sub_uid,
            "limit": limit,
        }
        if currency:
            params["currency"] = currency

        # Подписать параметры
        signed_params = self._sign("GET", endpoint, params)
        
        # Отправить запрос
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(endpoint, params=signed_params)
            
            # Обработка ответа
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("code") == 200:
                    print("@!!!\n")
                    return response_data.get("data", [])
                else:
                    print(f"Ошибка: {response_data.get('message')}")
                    return []
            else:
                print(f"HTTP ошибка: {response.status_code}, {response.text}")
                return []

    async def check_sub_account_payment(self, sub_uid: str, currency: str, amount:int):
        """
        Проверить, был ли выполнен депозит субаккаунта на нужную сумму.
        :param sub_uid: UID субаккаунта.
        :param currency: Валюта депозита (например, "usdt").
        :return: True, если депозит в состоянии "safe", иначе False.
        """
        deposit_amount = None

        deposits = await self.get_sub_deposit_history(sub_uid, currency)
        print(f"Депозиты: {deposits}, Тип: {type(deposits)}")

        for deposit in deposits:
            deposit_amount = float(deposit.get("amount", 0))
            deposit_state = deposit.get("state")

            if deposit_state == "safe" and deposit_amount >= amount:
                print(f"Депозит на сумму {deposit_amount} {currency} найден!")
                return 1
            else:
                print(f"Депозит на сумму {deposit_amount} {currency} ещё не подтверждён. Состояние: {deposit_state}")
                return 2

        print(f"Депозит на сумму {amount} {currency} не найден.")
        return 0

    
    async def get_sub_deposit_address(self, currency: str, sub_uid: str):
        """Получить адрес депозита для субаккаунта"""
        endpoint = "/v2/sub-user/deposit-address"
        
        # Параметры для запроса, включая идентификатор субаккаунта
        params = self._sign("GET", endpoint, {"currency": currency, "subUid": sub_uid})
        
        # Отладка параметров запроса
        print(f"Request params: {params}")
        
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(endpoint, params=params)
            
            if response.status_code == 200:
                response_data = response.json()  # Получаем JSON-данные
                print(f"Response: {response_data}")  # Печатаем ответ от сервера для отладки
                return response_data
            else:
                print(f"Error: {response.status_code}, {response.text}")
                return None

        
    async def get_deposit_history(self, currency: str):
        """Запрос истории депозитов"""
        endpoint = "/v1/query/deposit-withdraw"
        params = {
            "currency": currency,  # Валюта (например, 'usdt')
            "type": "deposit",      # Тип операции: депозит
            "size": "100"           # Количество записей для получения
        }
        
        # Подпись запроса
        signed_params = self._sign("GET", endpoint, params)
        
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(endpoint, params=signed_params)
            return response.json()
        
