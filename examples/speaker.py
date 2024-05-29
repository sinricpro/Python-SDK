import asyncio
from collections.abc import Callable
from numbers import Real
from typing import Final, Union

from sinric import SinricPro, SinricProConstants, SinricProTypes

APP_KEY: Final[str] = ''
APP_SECRET: Final[str] = ''
SPEAKER_ID: Final[str] = ''

CallbackFunctions = Union[
    Callable[[str, str], tuple[bool, str]],  # Power state / Set Mute
    Callable[[str, Real], tuple[bool, Real]],  # Set Volume
    Callable[[str, str, Real], tuple[bool,
                                     SinricProTypes.BandDictType]],  # Set Bands
    Callable[[str, str, Real, str], tuple[bool,
                                          SinricProTypes.BandDictType]],  # Adjust Bands
    Callable[[str, SinricProTypes.BandDictType,
              SinricProTypes.BandDictType, SinricProTypes.BandDictType], bool]  # Reset Bands
]


def power_state(device_id: str, state: str) -> tuple[bool, str]:
    print('device_id: {} lock state: {}'.format(device_id, state))
    return True, state


def set_bands(device_id: str, name: str, level: Real) -> tuple[bool, SinricProTypes.BandDictType]:
    print('device_id: {}, name: {}, name: {}'.format(device_id, name, level))
    return True, {'name': name, 'level': level}


def adjust_bands(device_id: str, name: str, level: Real, direction: str) -> tuple[bool, SinricProTypes.BandDictType]:
    # TODO direction should be an enum
    print('device_id: {}, name: {}, name: {}, direction: {}'.format(
        device_id, name, level, direction))
    return True, {'name': name, 'level': level}


def reset_bands(device_id: str, band1: SinricProTypes.BandDictType,
                band2: SinricProTypes.BandDictType, band3: SinricProTypes.BandDictType) \
        -> bool:
    print('device_id: {}, band1: {}, band2: {}, band3: {}'.format(
        device_id, band1, band2, band3))
    return True


def set_mode(device_id: str, mode: str) -> tuple[bool, str]:
    print('device_id: {} mode: {}'.format(device_id, mode))
    return True, mode


def set_mute(device_id: str, mute: str) -> tuple[bool, str]:
    # TODO: mute should be str? or a bool? or an enum?
    print('device_id: {} mute: {}'.format(device_id, mute))
    return True, mute


def set_volume(device_id: str, volume: Real) -> tuple[bool, Real]:
    print('device_id: {} volume: {}'.format(device_id, volume))
    return True, volume


callbacks: dict[str, CallbackFunctions] = {
    SinricProConstants.SET_POWER_STATE: power_state,
    SinricProConstants.SET_BANDS: set_bands,
    SinricProConstants.SET_MODE: set_mode,
    SinricProConstants.ADJUST_BANDS: adjust_bands,
    SinricProConstants.RESET_BANDS: reset_bands,
    SinricProConstants.SET_MUTE: set_mute,
    SinricProConstants.SET_VOLUME: set_volume
}

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    client = SinricPro(APP_KEY, [SPEAKER_ID], callbacks,
                       enable_log=False, restore_states=False, secret_key=APP_SECRET)
    loop.run_until_complete(client.connect())

# To update the speaker state on server.
# client.event_handler.raise_event(speakerId, SinricProConstants.SET_BANDS, data = {'name': '','level': 0})
