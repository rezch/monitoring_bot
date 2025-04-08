from config import TELEGRAM_API_TOKEN
from . import verify

import importlib.util
from os.path import dirname
from threading import Thread
from telebot import TeleBot


HANDLERS = ["notify"]

bot = None

if TELEGRAM_API_TOKEN:
    bot = TeleBot(TELEGRAM_API_TOKEN)


def bot_start_polling():
    if bot:
        handler_dir = dirname(__file__) + "/handlers/"
        for name in HANDLERS:
            spec = importlib.util.spec_from_file_location(name, f"{handler_dir}{name}.py")
            spec.loader.exec_module(importlib.util.module_from_spec(spec))

        bot.add_custom_filter(verify.IsAdminFilter())

        thread = Thread(target=bot.infinity_polling, daemon=True)
        thread.start()


from .handlers.notify import (
    report,
    report_to_admins,
    reply_to,
)

__all__ = [
    "bot",
    "report",
    "report_to_admins",
    "reply_to",
]
