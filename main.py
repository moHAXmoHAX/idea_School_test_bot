import random
from datetime import datetime
from time import time
import requests
import db
from aiogram import executor, types
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters import CommandStart
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ContentType, ReplyKeyboardRemove
from aiogram.utils.exceptions import MessageNotModified, MessageCantBeDeleted

from utils import dp, bot, on_startup, on_shutdown
from config import API_CURRENCY_URL
from keyboards import *

TMP = {}


# region FSM
class Button2(StatesGroup):
    name = State()
    gender = State()
    photo = State()
    menu_btn = State()


class Button5(StatesGroup):
    dbms = State()
    name = State()
    username = State()
    user_exist = State()
    name_edit = State()
    user_del = State()


# endregion


def get_time():
    return datetime.fromtimestamp(int(time()))


async def del_tmp_msg(user_id: int):
    while TMP[user_id].get('tmp_msg'):
        await bot.delete_message(chat_id=user_id,
                                 message_id=TMP[user_id]['tmp_msg'].pop())


@dp.message_handler(CommandStart(), state='*')
async def start_msg(msg: types.Message, state: FSMContext):
    await state.finish()
    start_message = await msg.answer(text="Список заданий",
                                     reply_markup=get_start_ikb())
    TMP.update({msg.from_id: {'tmp_msg': [], 'start_msg_id': start_message.message_id}})
    print(f"{get_time()}: {TMP}")


# region BUTTON 1
@dp.callback_query_handler(lambda c: c.data == 'start_keyboards', state='*')
async def menu_keyboard(clb: types.CallbackQuery):
    await clb.answer()
    username = f"@{clb.from_user.username}" if clb.from_user.username else clb.from_user.first_name
    await clb.message.edit_text(text=username,
                                reply_markup=get_menu_ikb())
    print(f"{get_time()}: {TMP}")


@dp.callback_query_handler(lambda c: c.data == 'cancel_ikb', state=Button5.dbms)
@dp.callback_query_handler(lambda c: c.data == 'start_menu', state='*')
async def menu_keyboard(clb: types.CallbackQuery, state: FSMContext):
    await clb.answer()
    await clb.message.edit_text(text="Список заданий",
                                reply_markup=get_start_ikb())
    await state.finish()

    print(f"{get_time()}: {TMP}")


# endregion


# region BUTTON 2
@dp.callback_query_handler(lambda c: c.data == 'start_fsm', state='*')
async def menu_fsm(clb: types.CallbackQuery):
    await clb.answer()
    await clb.message.edit_reply_markup(reply_markup=None)
    send_text = await clb.message.answer(text="Ведите имя", reply_markup=get_cancel_kb())
    TMP[clb.from_user.id].update({'tmp_msg': [clb.message.message_id, send_text.message_id]})
    await Button2.name.set()

    print(f"{get_time()}: {TMP}")


@dp.message_handler(filters.Text(equals='Отмена ❌'), state=Button2.name)
@dp.message_handler(filters.Text(equals='Отмена ❌'), state=Button2.gender)
@dp.message_handler(filters.Text(equals='Отмена ❌'), state=Button2.photo)
async def cancel_name(msg: types.Message, state: FSMContext):
    user_id = msg.from_id
    await del_tmp_msg(user_id=user_id)
    await msg.delete()
    await state.finish()
    await start_msg(msg=msg, state=state)

    print(f"{get_time()}: {TMP}")


@dp.message_handler(content_types=ContentType.TEXT, state=Button2.name)
async def get_name(msg: types.Message):
    TMP[msg.from_id].update({'user_name': msg.text})
    sex_msg = await msg.answer(text="Укажите ваш пол",
                               reply_markup=set_gender())
    TMP[msg.from_id]['tmp_msg'].append(msg.message_id)
    TMP[msg.from_id]['tmp_msg'].append(sex_msg.message_id)
    await Button2.gender.set()

    print(f"{get_time()}: {TMP}")


@dp.message_handler(filters.Text(contains='мужской') or filters.Text(contains='женский'), state=Button2.gender)
async def get_gender(msg: types.Message):
    TMP[msg.from_id].update({'gender': msg.text})
    get_photo_msg = await msg.answer(text="Загрузите ваше фото",
                                     reply_markup=get_cancel_kb())
    TMP[msg.from_id]['tmp_msg'].append(msg.message_id)
    TMP[msg.from_id]['tmp_msg'].append(get_photo_msg.message_id)
    await Button2.photo.set()

    print(f"{get_time()}: {TMP}")


@dp.message_handler(content_types=ContentType.PHOTO, state=Button2.photo)
async def get_photo(msg: types.Message):
    photo_id = msg.photo[-1].file_id
    user_id = msg.from_id
    name = TMP[user_id]['user_name']
    gender = TMP[user_id]['gender'].split(sep=' ')[-1]
    photo_msg = await bot.send_photo(chat_id=user_id,
                                     photo=photo_id,
                                     caption=f"Имя: <b>{name}</b>\n"
                                             f"Пол: <b>{gender}</b>",
                                     reply_markup=get_menu_kb())
    TMP[user_id].update({'photo_msg_id': photo_msg.message_id})
    await Button2.menu_btn.set()

    print(f"{get_time()}: {TMP}")


@dp.message_handler(filters.Text(equals='Меню'), state=Button2.menu_btn)
async def finish_btn2(msg: types.Message, state: FSMContext):
    user_id = msg.from_id
    await msg.delete()
    _ = await msg.answer(text="Загрузка главного меню...",
                         reply_markup=ReplyKeyboardRemove())
    await bot.delete_message(chat_id=user_id,
                             message_id=_.message_id)
    await start_msg(msg=msg, state=state)

    print(f"{get_time()}: {TMP}")


# endregion


# region BUTTON 3
@dp.callback_query_handler(lambda c: c.data == 'start_pay', state='*')
async def menu_pay(clb: types.CallbackQuery):
    await clb.answer(text="Develop",
                     show_alert=True)

    print(f"{get_time()}: {TMP}")
# endregion


# region BUTTON 4
@dp.callback_query_handler(lambda c: c.data == 'start_api', state='*')
async def menu_fsm(clb: types.CallbackQuery):
    await clb.answer(text="Загрузка курса валют...")
    currency = requests.get(url=API_CURRENCY_URL).json()
    try:
        await clb.message.edit_text(text=f"USD: <b>{currency['Valute']['USD']['Value']}</b>",
                                    reply_markup=get_start_ikb())
    except MessageNotModified:
        return

    print(f"{get_time()}: {TMP}")


# endregion


# region BUTTON 5
@dp.callback_query_handler(lambda c: c.data == 'start_dbms', state='*')
async def menu_dbms(clb: types.CallbackQuery):
    await clb.answer()
    await clb.message.edit_reply_markup(reply_markup=get_dbms_ikb())
    await Button5.dbms.set()

    print(f"{get_time()}: {TMP}")


@dp.callback_query_handler(lambda c: c.data == 'db_user_delete', state=Button5.dbms)
@dp.callback_query_handler(lambda c: c.data == 'db_new_user', state=Button5.dbms)
@dp.callback_query_handler(lambda c: c.data == 'db_user_edit', state=Button5.dbms)
async def send_get_name(clb: types.CallbackQuery):
    await clb.answer()
    user_id = clb.from_user.id
    name_msg = await clb.message.answer(text="Введите Имя:",
                                        reply_markup=get_cancel_kb())
    TMP[user_id]['tmp_msg'].append(name_msg.message_id)

    if clb.data == 'db_new_user':
        await Button5.name.set()
    elif clb.data == 'db_user_edit':
        await Button5.name_edit.set()
    elif clb.data == 'db_user_delete':
        await Button5.user_del.set()

    print(f"{get_time()}: {TMP}")


@dp.message_handler(filters.Text(equals='Отмена ❌'), state=Button5.name_edit)
@dp.message_handler(filters.Text(equals='Отмена ❌'), state=Button5.user_exist)
@dp.message_handler(filters.Text(equals='Отмена ❌'), state=Button5.name)
@dp.message_handler(filters.Text(equals='Отмена ❌'), state=Button5.username)
async def cancel_name(msg: types.Message, state: FSMContext):
    user_id = msg.from_id
    await del_tmp_msg(user_id=user_id)
    await bot.delete_message(chat_id=user_id, message_id=TMP[user_id]['start_msg_id'])
    await msg.delete()
    await state.finish()
    await start_msg(msg=msg, state=state)

    print(f"{get_time()}: {TMP}")


@dp.message_handler(content_types=ContentType.TEXT, state=Button5.name)
async def get_name(msg: types.Message):
    user_id = msg.from_id
    name = msg.text
    TMP[user_id]['tmp_msg'].append(msg.message_id)
    TMP[user_id].update({'name': name})

    user_name = await msg.answer(text="Введите username:")
    TMP[user_id]['tmp_msg'].append(user_name.message_id)

    await Button5.username.set()


@dp.message_handler(content_types=ContentType.TEXT, state=Button5.username)
async def get_username(msg: types.Message):
    user_id = msg.from_id
    username = msg.text
    name = TMP[user_id]['name']
    del TMP[user_id]['name']
    rand_num = random.randint(1, 100)

    await msg.delete()

    await db.create_user(name=name, username=username, rand_num=rand_num)
    try:
        await bot.edit_message_text(chat_id=user_id,
                                    message_id=TMP[user_id]['start_msg_id'],
                                    text="Пользователь добавлен",
                                    reply_markup=get_dbms_ikb())
    except MessageNotModified:
        pass
    await del_tmp_msg(user_id=user_id)
    await Button5.dbms.set()

    print(f"{get_time()}: {TMP}")


@dp.callback_query_handler(lambda c: c.data == 'db_user_exist', state=Button5.dbms)
async def send_get_username(clb: types.CallbackQuery):
    await clb.answer()
    user_id = clb.from_user.id
    username_msg = await clb.message.answer(text="Введите Username пользователя:",
                                            reply_markup=get_cancel_kb())
    TMP[user_id]['tmp_msg'].append(username_msg.message_id)
    await Button5.user_exist.set()

    print(f"{get_time()}: {TMP}")


@dp.message_handler(content_types=ContentType.TEXT, state=Button5.user_exist)
async def send_get_username(msg: types.Message):
    user_id = msg.from_id
    if_user = await db.user_exist(username=msg.text)
    if if_user:
        text = 'Пользователь есть в базе'
    else:
        text = 'Пользователь отсутствует'
    try:
        await bot.edit_message_text(chat_id=user_id,
                                    message_id=TMP[user_id]['start_msg_id'],
                                    text=text,
                                    reply_markup=get_dbms_ikb())
    except MessageNotModified:
        pass
    await del_tmp_msg(user_id=user_id)
    await msg.delete()
    await Button5.dbms.set()

    print(f"{get_time()}: {TMP}")


@dp.message_handler(content_types=ContentType.TEXT, state=Button5.name_edit)
async def user_update(msg: types.Message):
    name = msg.text
    user_id = msg.from_id
    TMP[user_id]['tmp_msg'].append(msg.message_id)

    if_user = await db.user_exist(name=name)
    print(if_user)
    if if_user:
        await db.update_user(name=name, new_name='Steve')
        await del_tmp_msg(user_id=user_id)
        try:
            await bot.edit_message_text(chat_id=user_id,
                                        message_id=TMP[user_id]['start_msg_id'],
                                        text="Имя изменено",
                                        reply_markup=get_dbms_ikb())
            await Button5.dbms.set()
        except MessageNotModified:
            await Button5.dbms.set()
            return
    else:
        await del_tmp_msg(user_id=user_id)
        try:
            await bot.edit_message_text(chat_id=user_id,
                                        message_id=TMP[user_id]['start_msg_id'],
                                        text="Пользователь отсутствует",
                                        reply_markup=get_dbms_ikb())
            await Button5.dbms.set()
        except MessageNotModified:
            await Button5.dbms.set()
            return

    print(f"{get_time()}: {TMP}")


@dp.message_handler(content_types=ContentType.TEXT, state=Button5.user_del)
async def user_delete(msg: types.Message):
    name = msg.text
    user_id = msg.from_id
    TMP[user_id]['tmp_msg'].append(msg.message_id)

    if_user = await db.user_exist(name=name)
    if if_user:
        await db.user_delete(name=name)
        await del_tmp_msg(user_id=user_id)
        try:
            await bot.edit_message_text(chat_id=user_id,
                                        message_id=TMP[user_id]['start_msg_id'],
                                        text="Пользователь удален",
                                        reply_markup=get_dbms_ikb())
            await Button5.dbms.set()
        except MessageNotModified:
            await Button5.dbms.set()
            return
    else:
        await del_tmp_msg(user_id=user_id)
        try:
            await bot.edit_message_text(chat_id=user_id,
                                        message_id=TMP[user_id]['start_msg_id'],
                                        text="Пользователь отсутствует",
                                        reply_markup=get_dbms_ikb())
            await Button5.dbms.set()
        except MessageNotModified:
            await Button5.dbms.set()
            return

    print(f"{get_time()}: {TMP}")


@dp.callback_query_handler(lambda c: c.data == 'db_get_num', state=Button5.dbms)
async def get_random(clb: types.CallbackQuery):
    await clb.answer()
    user_id = clb.from_user.id
    users_count = await db.get_users_count()
    random_user_id = random.randint(1, users_count)
    if_user = False
    while not if_user:
        if_user = await db.user_exist(user_id=random_user_id)
    rand_num = await db.get_user(user_id=random_user_id)
    print(rand_num)
    try:
        await bot.edit_message_text(chat_id=user_id,
                                    message_id=clb.message.message_id,
                                    text=f"rand_num: <b>{rand_num}</b>",
                                    reply_markup=get_dbms_ikb())
    except MessageNotModified:
        pass

    print(f"{get_time()}: {TMP}")

# endregion


# region BUTTON 6
@dp.callback_query_handler(lambda c: c.data == 'start_mg', state='*')
async def menu_fsm(clb: types.CallbackQuery):
    media = types.MediaGroup()
    media.attach_photo(types.InputFile('img/0.png'))
    media.attach_photo(types.InputFile('img/1.jpeg'))
    media.attach_photo(types.InputFile('img/2.jpg'))
    await bot.send_media_group(chat_id=clb.from_user.id,
                               media=media)
    await clb.answer()

    print(f"{get_time()}: {TMP}")


# endregion


# region PLUG
@dp.callback_query_handler(lambda c: c.message.chat.type == "private", state='*')
async def from_chat_clb(clb: types.CallbackQuery, state: FSMContext):
    print(await state.get_state())
    print("private")
    await clb.answer()


@dp.callback_query_handler(lambda c: c.message.chat.type == "channel", state='*')
async def from_chat_clb(clb: types.CallbackQuery):
    print("channel")
    await clb.answer()


@dp.message_handler(content_types=ContentType.ANY, state='*')
async def main(msg: types.Message):
    try:
        await msg.delete()
    except MessageCantBeDeleted:
        print(f"{get_time()}: ERROR:: MessageCantBeDeleted. User - {msg.from_id}, msg_id - {msg.message_id}")


# endregion


if __name__ == '__main__':
    executor.start_polling(dp,
                           skip_updates=True,
                           on_startup=on_startup,
                           on_shutdown=on_shutdown)
