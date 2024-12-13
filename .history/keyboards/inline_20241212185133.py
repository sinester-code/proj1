from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, callback_query
from aiogram.filters import callback_data
from aiogram.filters.callback_data import CallbackData



main = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Оформить подписку", callback_data="pay_sub"),
            InlineKeyboardButton(text="Проверка оповещения", callback_data="fff")
        ]
    ]
    
)

pays = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Btc", callback_data="cur_pay|btc"),
            InlineKeyboardButton(text="Usdt", callback_data="cur_pay|usdt")
        ],
        [
            InlineKeyboardButton(text="Trx", callback_data="cur_pay|trx"),
            InlineKeyboardButton(text="Litcoin", callback_data="cur_pay|ltc")
        ],
        [
            InlineKeyboardButton(text="Ton",callback_data="cur_pay|ton"),
            InlineKeyboardButton(text="Bnb",callback_data="cur_pay|bnb")
            
        ]
    ]
    
)

check = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Проверить", callback_data="check")
        ]
    ]
    
)