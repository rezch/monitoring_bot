from config import TELEGRAM_ADMIN_ID, TELEGRAM_LOGGER_CHANNEL_ID

from telebot import types
from telebot.custom_filters import SimpleCustomFilter
from telebot.types import Message


class IsAdminFilter(SimpleCustomFilter):
    key: str = "is_admin"

    def check(self, message: Message):
        if isinstance(message, types.CallbackQuery):
            return message.from_user.id in TELEGRAM_ADMIN_ID
        return message.chat.id == TELEGRAM_LOGGER_CHANNEL_ID or message.chat.id in TELEGRAM_ADMIN_ID
