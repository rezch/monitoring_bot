from telegram import bot, messages_queue, reply_to, send_stat

import asyncio
from typing import List


def admin_handler_wrapper(commands: List[str]):
    def wrapper(func):
        func = bot.channel_post_handler(commands=commands, is_admin=True)(func)
        func = bot.message_handler(commands=commands, is_admin=True)(func)
        return func
    return wrapper


@admin_handler_wrapper(commands=['stat'])
def stat_command(message):
    return send_stat(
        message,
        message.text.split('/stat ', 1)[-1].strip())


@admin_handler_wrapper(commands=['drop'])
def drop_command(message):
    command = message.text.split('/drop ', 1)[-1].strip()

    if command == 'msg queue':
        asyncio.run(messages_queue.drop_queue())
        return reply_to("Messages queue successfully dropped.", message)

    return reply_to("Unknown command.", message)
