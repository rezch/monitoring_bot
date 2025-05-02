from config import TELEGRAM_ADMIN_ID, TELEGRAM_LOGGER_CHANNEL_ID
from stats.prepare_stat import from_string, prepare_stat_image
from telegram import bot
from utils.tools import flatten

from datetime import timedelta
import logging
import os
from telebot.apihelper import ApiTelegramException
from telebot.types import Message
from typing import List


def _get_message_id(message: Message):
    if message.from_user is None:
        return message.chat.id
    return message.from_user.id


def check_bot_started_wrapper(call):
    def wrapper(*args, **kwargs):
        if bot is None or (not TELEGRAM_LOGGER_CHANNEL_ID and not TELEGRAM_ADMIN_ID):
            logging.error("Try report, while tokens or bot isn't set yet.")
            return []
        return call(*args, **kwargs)
    return wrapper


@check_bot_started_wrapper
def report_to_admins(text: str, parse_mode="html") -> List[Message]:
    if bot is None and not TELEGRAM_ADMIN_ID:
        logging.error("Try report, while tokens or bot isn't set yet.")
        return

    messages = []
    for admin in TELEGRAM_ADMIN_ID:
        try:
            messages.append(bot.send_message(admin, text, parse_mode))
            logging.info(f"SEND TO {admin}: {text}")
        except ApiTelegramException as e:
            logging.error(f'TGAPI ERR: {e}')

    return messages


@check_bot_started_wrapper
def report(text: str, parse_mode="html", fallback=True) -> List[Message]:
    if TELEGRAM_LOGGER_CHANNEL_ID:
        try:
            message = bot.send_message(TELEGRAM_LOGGER_CHANNEL_ID, text, parse_mode)
            logging.info(f"SEND TO {TELEGRAM_LOGGER_CHANNEL_ID} : {text}")
            return message
        except ApiTelegramException as e:
            logging.error(f'TGAPI ERR: {e}')

    if fallback:
        return report_to_admins(text, parse_mode)
    return []


@check_bot_started_wrapper
def reply_to(text: str, messages: Message | List[Message]) -> None:
    for message in flatten(messages):
        try:
            bot.reply_to(message, text)
            logging.info(f"REPLYED TO {_get_message_id(message)} : {text}")
        except ApiTelegramException as e:
            logging.error(f'TGAPI ERR: {e}')


def send_stat(reply_messages: Message | List[Message], resource_type: str) -> List[Message]:
    stat_collector = from_string(resource_type)

    if stat_collector is None:
        return reply_to(
            "Please, specify the resource type for collecting statistics.\n" + \
            "Unknown resource type. Use cpu/mem/net.",
            reply_messages)

    try:
        image_file = prepare_stat_image(
            timedelta(hours=3),
            stat_collector)

        callbacks = []
        with open(image_file, 'rb') as f:
            for message in flatten(reply_messages):
                callbacks.append(bot.send_photo(
                    message.chat.id,
                    f,
                    caption=stat_collector.description,
                    reply_to_message_id=message.message_id))

        os.remove(image_file)
        return callbacks
    except ZeroDivisionError as e:
        logging.error(f"TGAPI ERR: {e}")
        return reply_to(
            "Sorry, something went wrong...",
            reply_messages)
