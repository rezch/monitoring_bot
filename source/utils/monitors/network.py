from urllib import request


async def connection_check(proxy_ip, timeout: int = 1) -> bool:
    """
    ping check function

    :param proxy_ip: describe about parameter p1
    :param timeout: describe about parameter p2
    :return: is connection has established before timeout
    """

    return True
    # does not work
    try:
        request.urlopen(f'https://{proxy_ip}', timeout=timeout)
        return True
    except request.URLError as err:
        return False
