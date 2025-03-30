import alerts.alert_manager

import asyncio


if __name__ == "__main__":
    alert_handle = alerts.alert_manager.AlertManager()
    alert_handle.load_config()

    asyncio.run(alert_handle.run())