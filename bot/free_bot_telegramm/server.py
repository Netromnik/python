"""Сервер Telegram бота, запускаемый непосредственно"""
import logging
from aiogram import Bot, Dispatcher, executor
from setting import API_TOKEN
logging.basicConfig(level=logging.DEBUG)


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
from handler.common_type import *

from handler.comand import *

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)