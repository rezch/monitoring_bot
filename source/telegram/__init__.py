from config import TELEGRAM_API_TOKEN, STAT_IMAGE_PATH
from utils.coro import TaskQueue
from . import verify

import importlib.util
from os.path import dirname
from pathlib import Path
from threading import Thread
from telebot import TeleBot


bot = None
messages_queue = TaskQueue(
    delay=3, # min delay for telegram api
    sleep_delay=0.1,
    max_size=10)


if TELEGRAM_API_TOKEN:
    bot = TeleBot(TELEGRAM_API_TOKEN)


def quite_poll():
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            print(f'Polling err: {e}')


def message_queue_max_size_call():
    report("🟠 WARN: Too many messages queued.")


def bot_start_polling():
    HANDLERS = (
        "notify",
        "requests")

    if bot is None:
        print("Bot is not running")
        return

    Path(STAT_IMAGE_PATH).mkdir(parents=True, exist_ok=True)
    messages_queue.set_max_size_call(message_queue_max_size_call)

    bot.add_custom_filter(verify.IsAdminFilter())

    handler_dir = dirname(__file__) + "/handlers/"
    for name in HANDLERS:
        spec = importlib.util.spec_from_file_location(name, f"{handler_dir}{name}.py")
        spec.loader.exec_module(importlib.util.module_from_spec(spec))

    thread = Thread(target=quite_poll, daemon=True)
    thread.start()

    return thread


from .handlers.notify import (
    report,
    report_to_admins,
    reply_to,
    send_stat
)


__all__ = [
    "bot_start_polling",
    "messages_queue",
    "report",
    "report_to_admins",
    "reply_to",
    "send_stat",
]
