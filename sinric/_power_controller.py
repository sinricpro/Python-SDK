"""
 *  Copyright (c) 2019-2023 Sinricinricinricinricinric. All rights reserved.
 *  Licensed under Creative Commons Attribution-Share Alike (CC BY-SA)
 *
 *  This file is part of the Sinric Pro (https://github.com/sinricpro/)
"""

from collections.abc import Callable
from typing import Any
from ._sinricpro_constants import SinricProConstants


class PowerController:

    # TODO: Maybe define a type for json?
    async def power_state(self, jsn: Any, power_state_callback: Callable[[str, str], tuple[bool, str]]) -> tuple[bool, str]:
        return power_state_callback(jsn.get("payload").get(SinricProConstants.DEVICEID), jsn.get("payload").get("value").get("state"))
