import logging

from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ContentType

from server import dp
from state import get_state

log_i = logging.info
log_w = logging.warning



@dp.message_handler(content_types=ContentType.PHOTO)
async def text_valid(message: types.Message):
    state = get_state(message.from_user.id)
    log_i("WORK ?")
    state.set_photo(message.photo[-1].file_id)
    if len(state.get_photo()) > 3:
        await message.answer("Воспользуйтесь командой  /present_task для демонстрации ")

@dp.message_handler(content_types=ContentType.TEXT)
async def text_valid(message: types.Message):
    state = get_state(message.from_user.id)
    log_i(f"{state.__class__} ---{state.state}")
    if "text" == state.state:
        state.set_text(message.text)
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton("Отправить свою локацию 🗺️", request_location=True))
        markup.add("Вести вручную")
        await message.reply("Ведите геопазицию", reply_markup=markup)
    elif message.text == "Вести вручную":
        pass
    elif state.state == "geo":
        state.set_geo_link(message.text, 'text')
        await message.answer("Загрузите фото.Не более 3")
    # else:
    #     await message.answer("Произошел сбой в регистрации заявки для сброса заявки используйте /new_task")


@dp.message_handler(content_types=ContentType.LOCATION)
async def text_valid(message: types.Message):
    state = get_state(message.from_user.id)
    if state == 'geo':
        state.set_geo_link(message.location, "cord"),
    await message.answer("Загрузите фото.Не более 3\n По окончанию загрузки воспользуйтесь командой  /present_task")
