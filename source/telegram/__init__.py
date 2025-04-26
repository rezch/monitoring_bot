from config import TELEGRAM_API_TOKEN
from utils.coro import TaskQueue
from . import verify

import importlib.util
from os.path import dirname
from threading import Thread
from telebot import TeleBot


bot = None
messages_queue = TaskQueue(
    delay=3, # min delay for telegram api
    sleep_delay=0.1)


if TELEGRAM_API_TOKEN:
    bot = TeleBot(TELEGRAM_API_TOKEN)


# def quite_poll():
#     while True:
#         try:
#             bot.infinity_polling()
#         except Exception as e:
#             print(f'Polling err: {e}')


def bot_start_polling():
    HANDLERS = [
        "notify",
        "requests"]

    if bot:
        bot.add_custom_filter(verify.IsAdminFilter())

        handler_dir = dirname(__file__) + "/handlers/"
        for name in HANDLERS:
            spec = importlib.util.spec_from_file_location(name, f"{handler_dir}{name}.py")
            spec.loader.exec_module(importlib.util.module_from_spec(spec))

        thread = Thread(target=bot.infinity_polling, daemon=True)
        thread.start()

        return thread


from .handlers.notify import (
    report,
    report_to_admins,
    reply_to,
)

from .handlers.requests import (
    send_stat,
)

__all__ = [
    "bot_start_polling",
    "messages_queue",
    "report",
    "report_to_admins",
    "reply_to",
    "send_stat",
]
