from config import TELEGRAM_ADMIN_ID, TELEGRAM_LOGGER_CHANNEL_ID
from telegram import bot

import logging
from telebot.apihelper import ApiTelegramException
from telebot.types import Message
from typing import Iterable, List


def get_message_id(message: Message):
    if message.from_user.id is None:
        return message.chat.id
    return message.from_user.id


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
            logging.error(f'ERR: {e}')

    return messages


def report(text: str, parse_mode="html", fallback=True) -> List[Message]:
    if bot is None and not TELEGRAM_LOGGER_CHANNEL_ID:
        logging.error("Try report, while tokens or bot isn't set yet.")
        return []

    if TELEGRAM_LOGGER_CHANNEL_ID:
        try:
            message = bot.send_message(TELEGRAM_LOGGER_CHANNEL_ID, text, parse_mode)
            logging.info(f"SEND TO {TELEGRAM_LOGGER_CHANNEL_ID} : {text}")
            return [message]
        except ApiTelegramException as e:
            logging.error(f'ERR: {e}')

    if fallback:
        return report_to_admins(text, parse_mode)
    return []


def reply_to(text: str, messages: Message | List[Message]):
    if bot is None:
        logging.error("Try report, while tokens or bot isn't set yet.")
        return

    if not isinstance(messages, Iterable):
        messages = (messages, )

    for message in messages:
        try:
            bot.reply_to(message, text)
            logging.info(f"REPLYED TO {get_message_id} : {text}")
        except ApiTelegramException as e:
            logging.error(f'ERR: {e}')
