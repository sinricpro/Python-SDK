from collections.abc import Callable
from numbers import Real
from typing import Any, Final, Union
from sinric import SinricPro, SinricProConstants
import asyncio

APP_KEY: Final[str] = ''
APP_SECRET: Final[str] = ''
DEVICE_ID: Final[str] = ''

CallbackFunctions = Union[
    Callable[[str, str], tuple[bool, str]],  # Power state
    Callable[[str, Real, str], tuple[bool, Real, str]],  # Range Value
    Callable[[str, Any, str], tuple[bool, Any, str]]  # Mode Value
]


def power_state(device_id: str, state: str) -> tuple[bool, str]:
    print(device_id, state)
    return True, state


def range_value(device_id: str, range_value: Real, instance_id: str) -> tuple[bool, Real, str]:
    print(device_id, range_value, instance_id)
    return True, range_value, instance_id


def mode_value(device_id: str, mode_value: Any, instance_id: str) -> tuple[bool, Any, str]:
    # TODO: what is mode_Value? str?Enum?
    print(device_id, mode_value, instance_id)
    return True, mode_value, instance_id


callbacks: dict[str, CallbackFunctions] = {
    SinricProConstants.SET_POWER_STATE: power_state,
    SinricProConstants.SET_RANGE_VALUE: range_value,
    SinricProConstants.SET_MODE: mode_value
}

if __name__ == '__main__':
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    client: SinricPro = SinricPro(APP_KEY, [DEVICE_ID], callbacks,
                                  enable_log=False, restore_states=False, secret_key=APP_SECRET)
    loop.run_until_complete(client.connect())
