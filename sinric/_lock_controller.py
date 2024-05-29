"""
 *  Copyright (c) 2019-2023 Sinricinricinricinricinric. All rights reserved.
 *  Licensed under Creative Commons Attribution-Share Alike (CC BY-SA)
 *
 *  This file is part of the Sinric Pro (https://github.com/sinricpro/)
"""

from collections.abc import Callable
from typing import Any
from ._sinricpro_constants import SinricProConstants


class LockStateController:
    def __init__(self):
        self.lock_state: str = ''

    async def set_lock_state(self, jsn: Any, callback: Callable[[str, str], tuple[bool, str]]) -> tuple[bool, str]:
        return callback(jsn.get(SinricProConstants.DEVICEID), jsn.get("payload").get('value', False).get(SinricProConstants.STATE, "unlock"))
