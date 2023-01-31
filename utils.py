from config import *
from db import *
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

bot = Bot(token=BOT_API,
          parse_mode=types.ParseMode.HTML,
          disable_web_page_preview=True)
dp = Dispatcher(bot=bot,
                storage=MemoryStorage())


async def set_default_commands(dp: Dispatcher):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "В начало"),
            types.BotCommand("help", "Справка"),
            types.BotCommand("customer", "Профиль заказчика"),
            types.BotCommand("executor", "Профиль исполнителя"),
        ]
    )


async def on_startup(_):
    create_db()
    print("Bot is started!")
    # await set_default_commands(dp=dp)


async def on_shutdown(_):
    print("Bot is finished!")
