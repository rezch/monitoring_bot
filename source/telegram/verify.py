from config import TELEGRAM_ADMIN_ID

from telebot import types
from telebot.custom_filters import AdvancedCustomFilter


class IsAdminFilter(AdvancedCustomFilter):
    def check(self, message, text):
        if isinstance(message, types.CallbackQuery):
            return message.from_user.id in TELEGRAM_ADMIN_ID
        return message.chat.id in TELEGRAM_ADMIN_ID
