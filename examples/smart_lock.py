from collections.abc import Callable
from typing import Final
from sinric import SinricPro, SinricProConstants
import asyncio

APP_KEY: Final[str] = ''
APP_SECRET: Final[str] = ''
LOCK_ID: Final[str] = ''

CallbackFunctions = Callable[[str, str], tuple[bool, str]]


def lock_state(device_id: str, state: str) -> tuple[bool, str]:
    # TODO: state should definitely be an enum
    print('device_id: {} lock state: {}'.format(device_id, state))
    return True, state


callbacks: dict[str, CallbackFunctions] = {
    SinricProConstants.SET_LOCK_STATE: lock_state
}

if __name__ == '__main__':
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    client: SinricPro = SinricPro(APP_KEY, [LOCK_ID], callbacks, enable_log=False,
                                  restore_states=False, secret_key=APP_SECRET)
    loop.run_until_complete(client.connect())


# To update the lock state on server.
# client.event_handler.raise_event(LOCK_ID, SinricProConstants.SET_LOCK_STATE, data={
#                                  SinricProConstants.STATE: SinricProConstants.LOCK_STATE_LOCKED})
# client.event_handler.raise_eventttt(LOCK_ID, SinricProConstants.SET_LOCK_STATE, data={
#                                     SinricProConstants.STATE: SinricProConstants.LOCK_STATE_UNLOCKED})
