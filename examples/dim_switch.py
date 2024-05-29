from collections.abc import Callable
from numbers import Real
from typing import Final, Union
from sinric import SinricPro, SinricProConstants
import asyncio

APP_KEY: Final[str] = ''
APP_SECRET: Final[str] = ''
DIM_SWITCH_ID: Final[str] = ''

CallbackFunctions = Union[
    Callable[[str, str], tuple[bool, str]],  # Power state
    Callable[[str, Real], tuple[bool, Real]]  # Power Level
]


def power_state(device_id: str, state: str) -> tuple[bool, str]:
    print('device_id: {} state: {}'.format(device_id, state))
    return True, state


def power_level(device_id: str, power_level: Real) -> tuple[bool, Real]:
    print('device_id: {} power level: {}'.format(device_id, power_level))
    return True, power_level


callbacks: dict[str, CallbackFunctions] = {
    SinricProConstants.SET_POWER_STATE: power_state,
    SinricProConstants.SET_POWER_LEVEL: power_level
}

if __name__ == '__main__':
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    client: SinricPro = SinricPro(APP_KEY, [DIM_SWITCH_ID], callbacks,
                                  enable_log=False, restore_states=False, secret_key=APP_SECRET)
    loop.run_until_complete(client.connect())

    # client.event_handler.raise_event(DIM_SWITCH_ID, SinricProConstants.SET_POWER_LEVEL, data = {SinricProConstants.POWER_LEVEL: 50 })
    # client.event_handler.raise_event(DIM_SWITCH_ID, SinricProConstants.SET_POWER_STATE, data = {SinricProConstants.STATE: SinricProConstants.POWER_STATE_ON })
    # client.event_handler.raise_event(DIM_SWITCH_ID, SinricProConstants.SET_POWER_STATE, data = {SinricProConstants.STATE: SinricProConstants.POWER_STATE_OFF })
