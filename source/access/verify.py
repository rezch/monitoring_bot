def verify_id(uid: int) -> bool:
    WHITE_LIST = './whitelist'

    try:
        with open(WHITE_LIST, 'r') as f:
            while line := f.readline():
                verified_uid = int(line.split(' ', 1)[0].split('#', 1)[0])
                if uid == verified_uid:
                    return True
    except FileNotFoundError:
        # log(...)
        return False

    return False
