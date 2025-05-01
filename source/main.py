from alerts.alert_manager import AlertManager
from telegram import *

import asyncio


async def main():
    alert_handle = AlertManager()
    alert_handle.load_config()

    bot_thread = bot_start_polling()

    await asyncio.gather(
        alert_handle.run(),
        messages_queue.run())

    bot_thread.join()


if __name__ == "__main__":
    asyncio.run(main())
