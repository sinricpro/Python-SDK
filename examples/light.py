import asyncio
from collections.abc import Callable
from numbers import Real
from typing import Final, Union

from sinric import SinricPro, SinricProConstants

APP_KEY: Final[str] = ''
APP_SECRET: Final[str] = ''
LIGHT_ID: Final[str] = ''

CallbackFunctions = Union[
    Callable[[str, str], tuple[bool, str]],  # Power state
    # Set Brightness / Adjust Brightness
    Callable[[str, Real], tuple[bool, str]],
    Callable[[str, int, int, int], bool],  # Set Color
    Callable[[str, Real], bool],  # Set Color Temperature
    Callable[[str, Real], tuple[bool, Real]],  # Adjust Color Temperature
]


def power_state(device_id: str, state: str) -> tuple[bool, str]:
    print('device_id: {} state: {}'.format(device_id, state))
    return True, state


def set_brightness(device_id: str, brightness: Real) -> tuple[bool, Real]:
    print('device_id: {} brightness: {}'.format(device_id, brightness))
    return True, brightness


def adjust_brightness(device_id: str, brightness: Real) -> tuple[bool, Real]:
    print('device_id: {} adjusted brightness level: {}'.format(device_id, brightness))
    return True, brightness


# TODO: is there a bit type (0-256)?
def set_color(device_id: str, r: int, g: int, b: int) -> bool:
    print('device_id: {} R:{},G:{},B:{}'.format(device_id, r, g, b))
    return True


def set_color_temperature(device_id: str, color_temperature: Real) -> bool:
    print('device_id: {} color temperature:{}'.format(
        device_id, color_temperature))
    return True


def increase_color_temperature(device_id: str, value: Real) -> tuple[bool, Real]:
    print('device_id: {} value:{}'.format(device_id, value))
    return True, value


def decrease_color_temperature(device_id: str, value: Real) -> tuple[bool, Real]:
    print('device_id: {} value:{}'.format(device_id, value))
    return True, value


callbacks: dict[str, CallbackFunctions] = {
    SinricProConstants.SET_POWER_STATE: power_state,
    SinricProConstants.SET_BRIGHTNESS: set_brightness,
    SinricProConstants.ADJUST_BRIGHTNESS: adjust_brightness,
    SinricProConstants.SET_COLOR: set_color,
    SinricProConstants.SET_COLOR_TEMPERATURE: set_color_temperature,
    SinricProConstants.INCREASE_COLOR_TEMPERATURE: increase_color_temperature,
    SinricProConstants.DECREASE_COLOR_TEMPERATURE: decrease_color_temperature
}

if __name__ == '__main__':
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    client: SinricPro = SinricPro(APP_KEY, [LIGHT_ID], callbacks,
                                  enable_log=False, restore_states=False, secret_key=APP_SECRET)
    loop.run_until_complete(client.connect())

# To update the light state on server.
    # client.event_handler.raise_event(LIGHT_ID, SinricProConstants.SET_POWER_STATE, data = {SinricProConstants.STATE: SinricProConstants.POWER_STATE_ON })
    # client.event_handler.raise_event(LIGHT_ID, SinricProConstants.SET_POWER_STATE, data = {SinricProConstants.STATE: SinricProConstants.POWER_STATE_OFF })
    # client.event_handler.raise_event(LIGHT_ID, SinricProConstants.SET_COLOR, data = {SinricProConstants.RED: 0, SinricProConstants.GREEN: 0, SinricProConstants.BLUE: 0})
    # client.event_handler.raise_event(LIGHT_ID, SinricProConstants.SET_COLOR_TEMPERATURE, data={SinricProConstants.COLOR_TEMPERATURE: 2400})
