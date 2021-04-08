from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
import logging
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ContentType
from aiogram.dispatcher.filters import Text
from .fsm import Form
from config.conf import chat_id 
 
log_d = logging.debug

async def cmd_start(message: types.Message):
    """
    Hellow point
    """
    
    await message.answer(
        "Бот для  создания заявки для нарушения \n\n"
        "Начать создания заявки: /new_task\n"
        "Для отмены заявки: /cancel\n"
    )

async def cmd_cancel(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())

async def start_create_task(message: types.Message,state: FSMContext):
    """
    Start task entry point
    """
    # Cancel state and inform user about it
    await state.finish()

    # Set state
    await Form.text.set()
    await message.answer(
        "Опишите проблему (только текст одним сообщениям):"
    )

async def present_task(message: types.Message,state: FSMContext):
    async with state.proxy() as data:
        try:
            photo = data['photo']
            text = data["text"].lower()
            link = data["link"].lower()
        # And you can also use file ID:
        
            photo_split = photo.split(':')
            media = types.MediaGroup()
            for photo_id in photo_split:
                media.attach_photo(photo_id)
            # send media group
            await  message.reply_media_group(media=media)

            # send taks prevue
            await message.answer("*__Заявка__*\n" +
                                "*Сообщения*:{}\n".format(text)+
                                "*Место*:{}\n".format(link), parse_mode="MarkdownV2")
        except KeyError:
            await message.reply("Закончите заполнения формы или начните сначало")

async def send(message,state: FSMContext):
    async with state.proxy() as data:
        try:
            photo = data['photo']
            text = data["text"].lower()
            link = data["link"].lower()
        # And you can also use file ID:
            photo_split = photo.split(':')
            media = types.MediaGroup()
            for photo_id in photo_split:
                media.attach_photo(photo_id)
            # send media group
            await  message.bot.send_media_group(chat_id=chat_id, media=media)
            # send taks prevue
            await message.bot.send_message(chat_id=chat_id,text = "*__Заявка__*\n" +
                                "*Сообщения*:{}\n".format(text)+
                                "*Место*:{}\n".format(link), parse_mode="MarkdownV2")
        except KeyError:
            await message.reply("Закончите заполнения формы или начните сначало")

async def reload_state(message: types.Message,state: FSMContext):
    await state.previous()
    await message.reply("Ведите повторно",reply_markup=types.ReplyKeyboardRemove())

async def get_test(message: types.Message):
    chat_id = "-584307636"
    await message.reply(message.chat.id)

def register_handlers_common(dp):
    # Base command 
    dp.register_message_handler(cmd_start,commands='start')
    dp.register_message_handler(get_test,commands='ids')

    dp.register_message_handler(reload_state,commands='reload',state="*")
    dp.register_message_handler(cmd_cancel,commands='cancel',state="*")
    # command for task
    dp.register_message_handler(start_create_task,commands='new_task',state="*")
    dp.register_message_handler(present_task,commands='present_task',state="*")
    dp.register_message_handler(send,commands='send_task',state=Form.photo)
