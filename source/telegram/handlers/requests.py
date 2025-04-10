from telegram import bot
from telegram.handlers.notify import reply_to
from typing import List


def admin_handler_wrapper(commands: List[str]):
    def wrapper(func):
        func = bot.channel_post_handler(commands=commands, is_admin=True)(func)
        func = bot.message_handler(commands=commands, is_admin=True)(func)
        return func
    return wrapper


@admin_handler_wrapper(commands=['stat'])
def stat_command(message):
    # TODO
    return reply_to("stat", message)
