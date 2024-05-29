"""
 *  Copyright (c) 2019-2023 Sinric. All rights reserved.
 *  Licensed under Creative Commons Attribution-Share Alike (CC BY-SA)
 *
 *  This file is part of the Sinric Pro (https://github.com/sinricpro/)
"""

from collections.abc import Callable
from numbers import Real
from typing import Any, Union
from sinric.helpers.set_limits import set_limits
from ._sinricpro_constants import SinricProConstants
from ._types import SinricProTypes


class SpeakerController:

    def __init__(self):
        self.band: Real = 0

    async def set_bands(self, jsn: Any, callback: Callable[[str, str, Real], tuple[bool, SinricProTypes.BandDictType]]) \
            -> tuple[bool, SinricProTypes.BandDictType]:
        value = jsn.get("payload").get(SinricProConstants.VALUE)
        bands = value.get(SinricProConstants.BANDS)[0]
        return callback(jsn.get("payload").get(SinricProConstants.DEVICEID), bands.get(SinricProConstants.NAME), bands.get(SinricProConstants.LEVEL))

    async def adjust_bands(self, jsn: Any, callback: Callable[[str, str, Real, str], tuple[bool,
                                                                                           SinricProTypes.BandDictType]]) -> tuple[bool,
                                                                                                                                   SinricProTypes.BandDictType]:
        value = jsn.get("payload").get(SinricProConstants.VALUE)
        bands = value.get(SinricProConstants.BANDS)[0]
        self.band += bands.get(SinricProConstants.LEVEL_DELTA, 0)
        self.band = set_limits(self.band)
        return callback(jsn.get("payload").get(SinricProConstants.DEVICEID), bands.get(SinricProConstants.NAME), self.band,
                        bands.get(SinricProConstants.LEVELDIRECTION))

    async def reset_bands(self, jsn: Any, callback:    Callable[[str, SinricProTypes.BandDictType,
                                                                 SinricProTypes.BandDictType, SinricProTypes.BandDictType], bool]) -> bool:
        value = jsn.get("payload").get(SinricProConstants.VALUE)
        band1 = value.get(SinricProConstants.BANDS)[0]
        band2 = value.get(SinricProConstants.BANDS)[1]
        band3 = value.get(SinricProConstants.BANDS)[2]
        return callback(jsn.get("payload").get(SinricProConstants.DEVICEID), band1, band2, band3)
