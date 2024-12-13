from aiogram import Router, Bot, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State,StatesGroup
from aiogram.types import Message ,FSInputFile, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.types import InputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandObject
import config
import httpx
import sqlite3
from keyboards import inline
from datetime import timedelta
from fastapi import FastAPI, Depends
from database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from models import add_subscription, get_subscription, check_and_add_tg_id, get_uid_bd
from datetime import datetime, timedelta
from main import fetch_payment_address,check_payment_history, get_sub_address
from huobi_client import HuobiClient
from huobi.client.subuser import SubuserClient
from huobi.constant import *
from handlers.price_handler import get_price
from huobi.utils import *
import string
from handlers.subacc import create_subuser, check_deposit_history
import random
import string

API_KEY = config.PUB_KEY
SECRET_KEY = config.SEC_KEY

huobi_client = HuobiClient(api_key=API_KEY, secret_key=SECRET_KEY)

router = Router()

cur="usdt"
    

bot = Bot(config.TOKEN_BOT)



@router.callback_query(F.data == ( 'pay_sub'))
async def req_pay(call:CallbackQuery):
    await call.message.delete()
    x = await create_subuser(name = str(call.from_user.id))
    
    if x:
        result = await check_and_add_tg_id(tg_id=call.from_user.id, uid=x)
        print(result)
    else:
        print("Ошибка при создании sub-account")
    await call.message.answer("Выберите валюту",reply_markup=inline.pays)
    
@router.callback_query(F.data.startswith('check|'))
async def req_pay(call:CallbackQuery):
    parts = call.data.split("|")
    currency = parts[1]
    print(currency)
    await call.message.delete()
    uid = await get_uid_bd(tg_id=call.from_user.id)
    price = await get_price(currency)
    print(price)
    
    is_paid = await huobi_client.check_sub_account_payment(sub_uid=uid,currency=currency,amount=price)
    if is_paid == 2:
        await call.message.answer(text="Ваш платеж ожидает подтверждения!")
        
    elif is_paid == 1:
        await call.message.answer(text="Ваш платеж подтвержден! Подписка оформлена")
        await pay_sub_func(call=call)
        
    else:
        await call.message.answer(text="Ваш платеж пока-что не найден :(")



@router.callback_query()
async def process_currency_callback(callback: CallbackQuery):
    try:
        callback_data = callback.data

        parts = callback_data.split("|")
        if len(parts) == 2 and parts[0] == "cur_pay":
            await callback.message.delete()
            currency = parts[1]
            uid = await get_uid_bd(tg_id=callback.from_user.id)
            adres = await huobi_client.get_sub_deposit_address(sub_uid=uid, currency=currency)
            addresses_and_chains = [(entry['address'], entry['chain']) for entry in adres['data']]
            text = ""
            for f in addresses_and_chains:
                text += f"Адрес: {f[0]}\nСеть: {f[1]}\n\n"
            hh = await get_price(currency.upper())
            text=text+f"Пополняйте на любой из них {hh} и жмите 'Проверить'!" 
            
            check = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="Проверить", callback_data=f"check|{currency}")
                    ]
                ]
            )
            
            await callback.message.answer(text=text,reply_markup=check)
            
        else:
            await callback.message.answer("Некорректные данные в callback.")
    except Exception as e:
        await callback.message.answer(f"Ошибка обработки callback: {str(e)}")


async def pay_sub_func(call:CallbackQuery):
    
    user_id = call.from_user.id
    
    today = datetime.now().date()
    next_month = today + timedelta(days=30)

    date_start = today.isoformat()
    date_end = next_month.isoformat()

    async for session in get_session():
        sub = await add_subscription(session,user_id,date_start,date_end)
        await message.answer(text=f"Вы оформили подписку до {date_end.split('-')[2]} числа {date_end.split('-')[1]} месяца")
    
    async for name in config.ADMINS:
        await bot.send_message(chat_id=name,text=f"Пользователь: [{call.from_user.id}](t.me/{call.from_user.username}) оформил подписку!", parse_mode="Markdown")
        

    