from aiogram import Router, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State,StatesGroup
from aiogram.types import Message ,FSInputFile, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandObject
import config
import sqlite3
from keyboards import inline
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException
from hss import fetch_payment_address
from handlers.price_handler import get_price


app = FastAPI()


router = Router()
    
    
bot = Bot(config.TOKEN_BOT)


@router.message(CommandStart())
async def strt_cmd(message: Message):
    text = "Главное меню"
    await message.answer(text=text,reply_markup=inline.main)
    