import logging

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
import logging
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ContentType
from aiogram.dispatcher.filters import Text

log_d = logging.debug

# States
class Form(StatesGroup):
    text = State()
    geo = State()
    photo = State()

async def process_text(message: types.Message, state: FSMContext):
    """
    Process text date
    """
    async with state.proxy() as data:
        data['text'] = message.text
    
    # start markup geo state 
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("Отправить свою локацию 🗺️", request_location=True))
    markup.add("Вести вручную")
    await Form.next()
    await message.reply("Выберете способ ввода геопозиции", reply_markup=markup)


async def process_geo_text_check(message:types.Message, state:FSMContext):
    await state.update_data(flag_text_link="Ok")
    await message.reply("Выбранн ввод в ручную ( Введите адресс одним сообщениям ) \n Для повторного ввода используйте команду /reload")

async def process_geo_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if data.get('flag_text_link') == None:
            await message.reply("Пожалуйста, выберите метод ввода, используя клавиатуру ниже")
        else:
            log_d(message.location)
            data['link'] = message.text
            await Form.next()
            await message.reply("Загрузите фото (макс 3)\n\t После загрузки используйте команду для просмотра /present_task")


async def process_geo_link(message: types.Message, state: FSMContext):  
    async with state.proxy() as data:
            data['link'] = message.location
    await Form.next()
    await message.reply("Загрузите фото (макс 3)\n\t После загрузки используйте функцию для просмотра /present_task")
    
async def process_photo(message: types.Message,state: FSMContext):
    photo_list = ''
    async with state.proxy() as data:
        if data.get('photo') == None:
            data['photo'] =  message.photo[-1].file_id
        else:
            photo_list += "{}:{}".format(data['photo'],message.photo[-1].file_id) 
            data['photo'] = photo_list
        log_d(data.get('photo'))

def register_handlers_fsm(dp: Dispatcher):
    # text state 
    dp.register_message_handler(process_text,state=Form.text)
    # Geo state
    dp.register_message_handler(process_geo_text_check,Text(equals="Вести вручную", ignore_case=False), state=Form.geo)
    dp.register_message_handler(process_geo_text, state=Form.geo,content_types=ContentType.TEXT)
    dp.register_message_handler(process_geo_link, state=Form.geo,content_types=ContentType.LOCATION)
    # Photo get date
    dp.register_message_handler(process_photo,state=Form.photo, content_types=ContentType.PHOTO)

