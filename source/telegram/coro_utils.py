from . import messages_queue


def post_wrapper(call):
    def wrapper(*args, **kwargs):
        print("WRAPPED: ", call, args, kwargs)
        return messages_queue.post(call, args, kwargs)
    return wrapper
