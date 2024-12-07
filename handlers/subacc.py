from huobi.client.subuser import SubuserClient
from huobi.constant import *
from huobi.utils import *
import string
import random
from huobi.utils import LogInfo
# Конфигурация
API_KEY = "b1rkuf4drg-c73d0613-19797138-a8d2c"
SECRET_KEY = "1d9262a2-5f14b6cc-e1541743-75404"



async def create_subuser(name:str):
    subuser_client = SubuserClient(api_key=API_KEY, secret_key=SECRET_KEY)
    print(dir(subuser_client))
    userName = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
    name = "S"+name
    params = {"userList": [
        {
            "userName": name,
            "note": name
        }
    ]}

    try:
        userList = subuser_client.post_create_subuser(params)
        if isinstance(userList, list) and len(userList) > 0:
            user_data = userList[0]  # Получаем первый объект из списка
            # Проверяем, что объект имеет аттрибут uid
            if hasattr(user_data, 'uid'):
                return user_data.uid  # Возвращаем UID
            else:
                return "UID не найден в ответе"
        else:
            return "Ответ от API не содержит данных"
    except Exception as e:
        return str(e)
    
    
async def check_deposit_history(sub_id:int):
    subuser_client = SubuserClient(api_key=API_KEY, secret_key=SECRET_KEY)
    deposit_history = subuser_client.get_sub_user_deposit_history(sub_uid=sub_id)
    deposit_history.print_object()