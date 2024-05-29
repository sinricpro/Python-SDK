
import asyncio
from collections.abc import Callable
from numbers import Real
from typing import Final, Union

from sinric import SinricPro, SinricProConstants

CallbackFunctions = Union[
    Callable[[str, str], tuple[bool, str]],  # Power state
    Callable[[str, Real, str], tuple[bool, Real, str]]  # Range Value
]

APP_KEY: Final[str] = ''
APP_SECRET: Final[str] = ''
BLINDS_ID: Final[str] = ''

# TODO: got this from _sinricpro_constants.py - POWER_STATE_ON is a str, could we consider changing it to a strEnum?


def set_power_state(device_id: str, state: str) -> tuple[bool, str]:
    print('device_id: {} state: {}'.format(device_id, state))
    return True, state


def set_range_value(device_id: str, value: Real, instance_id: str) -> tuple[bool, Real, str]:
    print('device_id: {} set to: {}'.format(device_id, value))
    return True, value, instance_id


callbacks: dict[str, CallbackFunctions] = {
    SinricProConstants.SET_POWER_STATE: set_power_state,
    SinricProConstants.SET_RANGE_VALUE: set_range_value
}

if __name__ == '__main__':
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    client: SinricPro = SinricPro(APP_KEY, [BLINDS_ID], callbacks,
                                  enable_log=False, restore_states=False, secret_key=APP_SECRET)
    loop.run_until_complete(client.connect())

# client.event_handler.raise_event(BLINDS_ID, SinricProConstants.SET_RANGE_VALUE, data = {SinricProConstants.RANGE_VALUE: 30 })
# client.event_handler.raise_event(BLINDS_ID, SinricProConstants.SET_POWER_STATE, data = {SinricProConstants.STATE: SinricProConstants.POWER_STATE_ON })
# client.event_handler.raise_event(BLINDS_ID, SinricProConstants.SET_POWER_STATE, data = {SinricProConstants.STATE: SinricProConstants.POWER_STATE_OFF })
