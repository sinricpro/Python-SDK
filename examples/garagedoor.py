import asyncio
from collections.abc import Callable
from typing import Any, Final, Union

from sinric import SinricPro, SinricProConstants

APP_KEY: Final[str] = ''
APP_SECRET: Final[str] = ''
GARAGEDOOR_ID: Final[str] = ''

CallbackFunctions = Union[
    Callable[[str, str], tuple[bool, str]],  # Power state
    Callable[[str, Any, str], tuple[bool, Any, str]]  # Mode Value
]


def power_state(device_id: str, state: str) -> tuple[bool, str]:
    print('device_id: {} state: {}'.format(device_id, state))
    return True, device_id


def set_mode(device_id: str, state: Any, instance_id: str) -> tuple[bool, Any, str]:
    print('device_id: {} mode: {}'.format(device_id, state))
    return True, state, instance_id


callbacks:  dict[str, CallbackFunctions] = {
    SinricProConstants.SET_MODE: set_mode,
    SinricProConstants.SET_POWER_STATE: power_state
}

if __name__ == '__main__':
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    client: SinricPro = SinricPro(APP_KEY, [GARAGEDOOR_ID], callbacks,
                                  enable_log=False, restore_states=False, secret_key=APP_SECRET)
    loop.run_until_complete(client.connect())

    # client.event_handler.raise_event(GARAGEDOOR_ID, SinricProConstants.SET_MODE, data = {SinricProConstants.MODE: SinricProConstants.OPEN })
    # client.event_handler.raise_event(GARAGEDOOR_ID, SinricProConstants.SET_MODE, data = {SinricProConstants.MODE: SinricProConstants.CLOSE })
