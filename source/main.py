from alerts.alert_manager import AlertManager
from telegram import bot_start_polling

import asyncio


async def main():
    alert_handle = AlertManager()
    alert_handle.load_config()

    bot_start_polling()
    alert_coro = asyncio.create_task(
        alert_handle.run())
    
    await alert_coro


if __name__ == "__main__":
    asyncio.run(main())
