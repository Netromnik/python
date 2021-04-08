import logging

from aiogram import types
from aiogram.types import ParseMode
from aiogram.utils.markdown import text, bold

from server import dp, bot
from state import drop_task_state, get_state

log_i = logging.info
log_w = logging.warning


@dp.message_handler(commands=['start', 'help'])
async def hello(message: types.Message):
    await message.answer(
        "Бот для  создания заявки для нарушения \n\n"
        "Начать создания заявки: /new_task\n"
    )


@dp.message_handler(commands=['new_task', ])
async def task_start(message: types.Message):
    drop_task_state(message.from_user.id)
    get_state(message.from_user.id)
    await message.answer("Ведите текст")


@dp.message_handler(commands=["present_task", ])
async def present_task(message: types.Message):
    state = get_state(message.from_user.id)
    photo = state.session['photo']
    # And you can also use file ID:
    if photo != None:
        photo_split = photo.split(';')
        media = types.MediaGroup()
        for photo_id in photo_split:
            media.attach_photo(photo_id, 'cat-cat-cat.')
        await  message.reply_media_group(media=media)

    await message.answer(text(bold("Внешний вид заявки", '\n'),
                              bold("Текст", ":"),
                              state.session["body_text"], '\n',
                              bold("Местоположения", ":"),
                              state.session["locate"].split(":")[1], "\n\n",
                              "Для отправки заявки воспользуйтесь /send\_task\n\n\n",
                              "Для сброса заявки используйте: /drop\_task"
                              ), parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(commands=["send_task"])
async def send(message: types.Message):
    log_i(f"Chat id{message.chat.id}")
    chat_id = "@why_name_bot"
    state = get_state(message.from_user.id)
    photo = state.session['photo']
    # And you can also use file ID:
    if photo != None:
        photo_split = photo.split(';')
        media = types.MediaGroup()
        for photo_id in photo_split:
            media.attach_photo(photo_id, 'cat-cat-cat.')
        await  bot.send_media_group(chat_id=chat_id, media=media)
    await bot.send_message(chat_id=chat_id, message=text(bold("Внешний вид заявки", '\n'),
                                                         bold("Текст", ":"),
                                                         state.session["body_text"], '\n',
                                                         bold("Местоположения", ":"),
                                                         state.session["locate"].split(":")[1], "\n\n",
                                                         "Для отправки заявки воспользуйтесь /send\_task\n\n\n",
                                                         "Для сброса заявки используйте: /drop\_task"
                                                         ), parse_mode=ParseMode.MARKDOWN)
