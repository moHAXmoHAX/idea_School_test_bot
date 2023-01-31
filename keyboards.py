from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_start_ikb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup()
    ikb.add(InlineKeyboardButton(text="Клавиатуры", callback_data="start_keyboards"))
    ikb.add(InlineKeyboardButton(text="Машинное состояние", callback_data="start_fsm"))
    ikb.add(InlineKeyboardButton(text="Платежная система", callback_data="start_pay"))
    ikb.add(InlineKeyboardButton(text="API", callback_data="start_api"))
    ikb.add(InlineKeyboardButton(text="СУБД", callback_data="start_dbms"))
    ikb.add(InlineKeyboardButton(text="Медиа группы", callback_data="start_mg"))
    return ikb


def get_cancel_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton(text="Отмена ❌"))
    return kb


def get_menu_ikb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup().add(InlineKeyboardButton(text="Меню", callback_data="start_menu"))


def get_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(resize_keyboard=True).add(InlineKeyboardButton(text="Меню"))


def set_gender() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton(text="🙎‍♂️ мужской"))
    kb.insert(KeyboardButton(text="🙍‍♀️ женский"))
    kb.add(KeyboardButton(text="Отмена ❌"))
    return kb


def get_dbms_ikb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup()
    ikb.add(InlineKeyboardButton(text="Добавить пользователя в БД", callback_data="db_new_user"))
    ikb.add(InlineKeyboardButton(text="Проверить на наличие пользователя", callback_data="db_user_exist"))
    ikb.add(InlineKeyboardButton(text="Изменить имя пользователя", callback_data="db_user_edit"))
    ikb.add(InlineKeyboardButton(text="Удалить пользователя", callback_data="db_user_delete"))
    ikb.add(InlineKeyboardButton(text="Получить число", callback_data="db_get_num"))
    ikb.add(InlineKeyboardButton(text="Назад", callback_data="cancel_ikb"))
    return ikb
