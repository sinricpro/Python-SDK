from typing import Any, Final
from sinric import SinricPro, SinricProConstants
import asyncio
from asyncio import sleep

APP_KEY: Final[str] = ''
APP_SECRET: Final[str] = ''
TEMPERATURE_SENSOR_ID: Final[str] = ''


async def events():
    while True:
        # client.event_handler.raise_event(TEMPERATURE_SENSOR_ID,
        #                                  SinricProConstants.CURRENT_TEMPERATURE,
        #                                  data= { SinricProConstants.HUMIDITY: 75.3, SinricProConstants.TEMPERATURE: 24})
        # client.event_handler.raise_event(TEMPERATURE_SENSOR_ID, SinricProConstants.SET_POWER_STATE, data= {SinricProConstants.STATE: SinricProConstants.POWER_STATE_ON})
        # client.event_handler.raise_event(TEMPERATURE_SENSOR_ID, SinricProConstants.SET_POWER_STATE, data= {SinricProConstants.STATE: SinricProConstants.POWER_STATE_OFF})
        # Server will trottle / block IPs sending events too often.
        await sleep(60)

callbacks: dict[str, Any] = {}

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    client = SinricPro(APP_KEY, [TEMPERATURE_SENSOR_ID], callbacks, event_callbacks=events,
                       enable_log=True, restore_states=False, secret_key=APP_SECRET)
    loop.run_until_complete(client.connect())

# To update the temperature on the server.
# client.event_handler.raise_event(temperatureSensorDeviceId, SinricProConstants.CURRENT_TEMPERATURE, data={'humidity': 75.3, 'temperature': 24})
