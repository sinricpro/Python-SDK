"""
 *  Copyright (c) 2019-2023 Sinric. All rights reserved.
 *  Licensed under Creative Commons Attribution-Share Alike (CC BY-SA)
 *
 *  This file is part of the Sinric Pro (https://github.com/sinricpro/)
"""

from numbers import Real
from typing import Any, Callable
from sinric.helpers.set_limits import set_limits
from ._sinricpro_constants import SinricProConstants

SetRangeCallbackType = Callable[[str, Real, str], tuple[bool, Real, str]]
# TODO: Should this return tuple[bool, Real]?
AdjustRangeCallbackType = Callable[[str, Real], Any]


class RangeValueController:
    def __init__(self, range_value: Real):
        self.range_value: Real = range_value
        self.instance_id: str = ''

    async def set_range_value(self, jsn: Any, range_callback: SetRangeCallbackType) -> tuple[bool, Real, str]:
        self.range_value = jsn.get("payload").get(
            SinricProConstants.VALUE).get(SinricProConstants.RANGE_VALUE)
        self.instance_id = jsn.get("payload").get(
            SinricProConstants.INSTANCE_ID, '')
        return range_callback(jsn.get("payload").get(SinricProConstants.DEVICEID), self.range_value, self.instance_id)

    # TODO Match return type with callback function
    async def adjust_range_value(self, jsn: Any, callback: AdjustRangeCallbackType) -> Any:
        self.range_value += jsn.get("payload").get(
            SinricProConstants.VALUE).get(SinricProConstants.RANGE_VALUE)
        self.range_value = set_limits(self.range_value)
        return callback(jsn.get("payload").get(SinricProConstants.DEVICEID), self.range_value)
