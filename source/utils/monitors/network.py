import subprocess


async def connection_check(proxy_ip, timeout: int = 1) -> bool:
    """
    ping check function

    :param proxy_ip: describe about parameter p1
    :param timeout: describe about parameter p2
    :return: is connection has established before timeout
    """

    command = f'ping -c 1 {proxy_ip}'

    p = subprocess.Popen(
        command.split(' '),
        stdout=subprocess.DEVNULL)

    try:
        p.wait(timeout)
        return True
    except subprocess.TimeoutExpired:
        p.kill()

    return False
