"""
 *  Copyright (c) 2019-2023 Sinric. All rights reserved.
 *  Licensed under Creative Commons Attribution-Share Alike (CC BY-SA)
 *
 *  This file is part of the Sinric Pro (https://github.com/sinricpro/)
"""

from collections.abc import Callable
from numbers import Real
from typing import Any

from sinric.helpers.set_limits import set_limits

from ._sinricpro_constants import SinricProConstants


class BrightnessController:
    def __init__(self, brightness_level: Real) -> None:
        self.brightness_level: Real = brightness_level

    async def set_brightness(self, jsn: Any, brightness_callback: Callable[[str, Real], tuple[bool, str]]) -> tuple[bool, str]:
        self.brightness_level = jsn.get("payload").get(
            SinricProConstants.VALUE).get(SinricProConstants.BRIGHTNESS)
        return brightness_callback(jsn.get("payload").get(SinricProConstants.DEVICEID), self.brightness_level)

    async def adjust_brightness(self, jsn, brightness_callback: Callable[[str, Real], tuple[bool, str]]) -> tuple[bool, str]:
        self.brightness_level += jsn.get("payload").get(
            SinricProConstants.VALUE).get(SinricProConstants.BRIGHTNESS_DELTA)
        self.brightness_level = set_limits(self.brightness_level)

        return brightness_callback(jsn.get("payload").get(SinricProConstants.DEVICEID), self.brightness_level)
