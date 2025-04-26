from stats.prepare_stat import CpuStat, MemStat, NetStat, prepare_stat_image
from telegram import bot, reply_to
from telegram.coro_utils import fetch_message, post_wrapper
from telegram.handlers.notify import force_reply_to
from utils.tools import flatten

from datetime import timedelta
import logging
import os
from telebot.types import Message
from typing import List


def admin_handler_wrapper(commands: List[str]):
    def wrapper(func):
        func = bot.channel_post_handler(commands=commands, is_admin=True)(func)
        func = bot.message_handler(commands=commands, is_admin=True)(func)
        return func
    return wrapper


def uncoro_send_stat(reply_messages: Message | List[Message], resource_type: str):
    stat_collector = None
    if resource_type == 'cpu':
        stat_collector = CpuStat
    elif resource_type == 'mem':
        stat_collector = MemStat
    elif resource_type == 'net':
        stat_collector = NetStat

    if stat_collector is None:
        return reply_to(
            "Unknown resource type. Use cpu/mem/net.",
            reply_messages)

    try:
        image_file = prepare_stat_image(
            timedelta(hours=3),
            stat_collector)

        with open(image_file, 'rb') as f:
            for message in flatten(reply_messages):
                callback = bot.send_photo(
                    message.chat.id,
                    f,
                    caption=stat_collector.description,
                    reply_to_message_id=message.message_id)

        os.remove(image_file)

        return callback
    except ZeroDivisionError as e:
        logging.error(f"ERR: {e}")
        return reply_to(
            "Sorry, something went wrong...",
            reply_messages)


@post_wrapper
async def send_stat(reply_messages: Message | List[Message], resource_type: str):
    return send_stat(fetch_message(reply_messages), resource_type)


@admin_handler_wrapper(commands=['stat'])
def stat_command(message):
    resource_type = message.text.split('/stat ', 1)

    if len(resource_type) == 1:
        return force_reply_to(
            "Please, specify the resource type for collecting statistics.",
            message)

    resource_type = resource_type[1].strip()

    return uncoro_send_stat(message, resource_type)
