from config import TELEGRAM_ADMIN_ID, TELEGRAM_LOGGER_CHANNEL_ID
from telegram import bot
from telegram.coro_utils import post_wrapper
from utils.tools import flatten
from utils.coro import fetch_message

import asyncio
import logging
from telebot.apihelper import ApiTelegramException
from telebot.types import Message
from time import sleep
from typing import List


def get_message_id(message: Message):
    if message.from_user.id is None:
        return message.chat.id
    return message.from_user.id


@post_wrapper
async def report_to_admins(text: str, parse_mode="html") -> List[Message]:
    if bot is None and not TELEGRAM_ADMIN_ID:
        logging.error("Try report, while tokens or bot isn't set yet.")
        return

    messages = []

    for admin in TELEGRAM_ADMIN_ID:
        try:
            messages.append(bot.send_message(admin, text, parse_mode))
            logging.info(f"SEND TO {admin}: {text}")
        except ApiTelegramException as e:
            if 'Error code: 429' in e:
                sleep(1)
                return report_to_admins(text, parse_mode)
            logging.error(f'ERR: {e}')

    return messages


@post_wrapper
async def report(text: str, parse_mode="html", fallback=True) -> List[Message]:
    if bot is None and not TELEGRAM_LOGGER_CHANNEL_ID:
        logging.error("Try report, while tokens or bot isn't set yet.")
        return []

    if TELEGRAM_LOGGER_CHANNEL_ID:
        try:
            message = bot.send_message(TELEGRAM_LOGGER_CHANNEL_ID, text, parse_mode)
            logging.info(f"SEND TO {TELEGRAM_LOGGER_CHANNEL_ID} : {text}")
            return [message]
        except ApiTelegramException as e:
            if 'Error code: 429' in e:
                await asyncio.sleep(1)
                return report(text, parse_mode, fallback)
            logging.error(f'ERR: {e}')

    if fallback:
        return report_to_admins(text, parse_mode)
    return []


@post_wrapper
def reply_to(text: str, messages: Message | List[Message]):
    if bot is None:
        logging.error("Try report, while tokens or bot isn't set yet.")
        return

    for message in flatten(messages):
        try:
            bot.reply_to(fetch_message(message), text)
            logging.info(f"REPLYED TO {get_message_id} : {text}")
        except ApiTelegramException as e:
            if 'Error code: 429' in e:
                sleep(1)
                return reply_to(text, messages)
            logging.error(f'ERR: {e}')


def force_reply_to(text: str, messages: Message | List[Message]):
    if bot is None:
        logging.error("Try report, while tokens or bot isn't set yet.")
        return

    for message in flatten(messages):
        try:
            bot.reply_to(message, text)
            logging.info(f"REPLYED TO {get_message_id} : {text}")
        except ApiTelegramException as e:
            if 'Error code: 429' in e:
                sleep(1)
                return reply_to(text, messages)
            logging.error(f'ERR: {e}')
