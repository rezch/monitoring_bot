from decouple import config
from dotenv import load_dotenv


load_dotenv()


TELEGRAM_API_TOKEN = config("TELEGRAM_API_TOKEN", default="")
TELEGRAM_ADMIN_ID = config(
    "TELEGRAM_ADMIN_ID",
    default="",
    cast=lambda v: [int(i) for i in filter(str.isdigit, (s.strip() for s in v.split(',')))])
TELEGRAM_LOGGER_CHANNEL_ID = config("TELEGRAM_LOGGER_CHANNEL_ID", cast=int, default=0)

PROXY_IP = config(
    "PROXY_IP",
    cast=lambda s: s.strip(),
    default="")

LOG_PATH = config("LOG_PATH", default="/var/log/monitor")
LOG_CAPACITY = config("LOG_CAPACITY", cast=int, default=1000)
