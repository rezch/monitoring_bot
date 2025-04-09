import subprocess


x = 0
def connection_check(proxy_ip, timeout: int = 1) -> bool:
    global x
    p = subprocess.Popen(['ping', '-c', '1', str(proxy_ip)])
    try:
        p.wait(timeout)
        return True
    except subprocess.TimeoutExpired:
        p.kill()

    x += 1
    if x == 2:
        return True

    return False
