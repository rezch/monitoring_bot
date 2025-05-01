from telegram import *
from .structs import AlertGroups, PackagedMessage

from functools import partial


def callback_post_wrapper(func):
    async def wrapper(*args):
        return await messages_queue.post(
            PackagedMessage(func, args))
    return wrapper


def get_callback(groups: AlertGroups):
    if groups == AlertGroups.ALL:
        return callback_post_wrapper(
            report)
    if groups == AlertGroups.CHANNEL:
        return callback_post_wrapper(
            partial(report, fallback=False))
    if groups == AlertGroups.ADMINS:
        return callback_post_wrapper(
            report_to_admins)


async def coro_send_stat(reply_messages, resource_type):
    await messages_queue.post(PackagedMessage(
            send_stat,
            reply_messages, resource_type))
