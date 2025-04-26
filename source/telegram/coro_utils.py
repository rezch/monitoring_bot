from utils.coro import fetch_message
from . import messages_queue


def post_wrapper(call):
    def wrapper(*args, **kwargs):
        args = fetch_message(args)
        kwargs = fetch_message(kwargs)
        return messages_queue.post(
            call, args, kwargs)
    return wrapper
