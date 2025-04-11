from stats.prepare_stat import CpuStat, MemStat, NetStat, prepare_stat_image
from telegram import bot
from telegram.handlers.notify import reply_to

from datetime import timedelta
import logging
import os
from typing import List


def admin_handler_wrapper(commands: List[str]):
    def wrapper(func):
        func = bot.channel_post_handler(commands=commands, is_admin=True)(func)
        func = bot.message_handler(commands=commands, is_admin=True)(func)
        return func
    return wrapper


@admin_handler_wrapper(commands=['stat'])
def stat_command(message):
    resource_type = message.text.split('/stat ', 1)

    if len(resource_type) == 1:
        return reply_to(
            "Please, specify the resource type for collecting statistics.",
            message)

    resource_type = resource_type[1].strip()

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
            message)

    try:
        image_file = prepare_stat_image(
            timedelta(hours=1),
            stat_collector)
        
        with open(image_file, 'rb') as f:
            callback = bot.send_photo(
                message.chat.id,
                f,
                caption=stat_collector.description,
                reply_to_message_id=message.message_id)

        os.remove(image_file)

        return callback
    except Exception as e:
        logging.error(f"ERR: {e}")
        return reply_to(
            "Sorry, something went wrong...",
            message)
