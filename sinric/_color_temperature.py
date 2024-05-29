"""
 *  Copyright (c) 2019-2023 Sinric. All rights reserved.
 *  Licensed under Creative Commons Attribution-Share Alike (CC BY-SA)
 *
 *  This file is part of the Sinric Pro (https://github.com/sinricpro/)
"""


from collections.abc import Callable
from numbers import Real
from typing import Any


class ColorTemperatureController:
    def __init__(self, temperatures_index: Real, temperatures_array: list[Real]) -> None:
        self.temperatures_index: Real = temperatures_index
        self.temperatures_array: list[Real] = temperatures_array

    async def set_color_temperature(self, jsn: Any, set_callback: Callable[[str, Real], bool]) -> bool:
        return set_callback(jsn.get("payload").get("deviceId"),
                            jsn.get("payload").get("value").get("colorTemperature"))

    async def increase_color_temperature(self, jsn: Any, increase_callback: Callable[[str, Real], tuple[bool, Real]]) -> tuple[bool, Real]:
        return increase_callback(jsn.get("payload").get("deviceId"), jsn.get("payload").get("value"))

    async def decrease_color_temperature(self, jsn: Any, decrease_callback: Callable[[str, Real], tuple[bool, Real]]) -> tuple[bool, Real]:
        return decrease_callback(jsn.get("payload").get("deviceId"), jsn.get("payload").get("value"))
