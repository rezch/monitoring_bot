from config import TELEGRAM_ADMIN_ID, TELEGRAM_LOGGER_CHANNEL_ID
from telegram import bot

import logging
from telebot.apihelper import ApiTelegramException
from telebot.types import Message
from typing import List


def get_log_id_from_message(message: Message):
    if message.from_user.id is None:
        return message.chat.id
    return message.from_user.id

def report_to_admins(text: str, parse_mode="html") -> List[Message]:
    if bot is None or not TELEGRAM_ADMIN_ID:
        logging.error("Try report, while tokens or bot isn't set yet.")
        return

    recipients_ids = str()
    messages = []

    for admin in TELEGRAM_ADMIN_ID:
        try:
            messages.append(bot.send_message(
                admin, text, parse_mode=parse_mode))
            recipients_ids += f"{admin} "
        except ApiTelegramException as e:
            logging.error(f'ERR: {e}')

    logging.info(f"SEND TO {recipients_ids}: {text}")
    return messages


def report(text: str, parse_mode="html") -> List[Message]:
    if bot is None or not TELEGRAM_LOGGER_CHANNEL_ID:
        logging.error("Try report, while tokens or bot isn't set yet.")
        return

    try:
        if TELEGRAM_LOGGER_CHANNEL_ID:
            message = bot.send_message(TELEGRAM_LOGGER_CHANNEL_ID, text, parse_mode=parse_mode)
            logging.info(f"SEND TO {TELEGRAM_LOGGER_CHANNEL_ID} : {text}")
            return message
        return report_to_admins(text, parse_mode)
    except ApiTelegramException as e:
        logging.error(f'ERR: {e}')


def reply_to(text: str, messages: List[Message], parse_mode="html"):
    if bot is None:
        logging.error("Try report, while tokens or bot isn't set yet.")
        return

    for message in messages:
        try:
            bot.reply_to(message, text, parse_mode)
            logging.info(f"REPLYED TO {get_log_id_from_message} : {text}")
        except ApiTelegramException as e:
            logging.error(f'ERR: {e}')
