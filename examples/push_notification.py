from typing import Final
from sinric import SinricPro, SinricProConstants
import asyncio
from asyncio import sleep

APP_KEY: Final[str] = ''
APP_SECRET: Final[str] = ''
DEVICE_ID: Final[str] = ''


async def events():
    while True:
        client.event_handler.raise_event(
            DEVICE_ID, SinricProConstants.PUSH_NOTIFICATION, data={'alert': "Hello there"})
        # Server will trottle / block IPs sending events too often.
        await sleep(60)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    client = SinricPro(APP_KEY, [DEVICE_ID], {}, event_callbacks=events,
                       enable_log=True, restore_states=False, secret_key=APP_SECRET)
    loop.run_until_complete(client.connect())
