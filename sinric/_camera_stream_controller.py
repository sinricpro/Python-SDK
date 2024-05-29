"""
 *  Copyright (c) 2019-2023 Sinric. All rights reserved.
 *  Licensed under Creative Commons Attribution-Share Alike (CC BY-SA)
 *
 *  This file is part of the Sinric Pro (https://github.com/sinricpro/)
"""

from collections.abc import Callable
from typing import Any, ByteString, Optional, Union
from ._sinricpro_constants import SinricProConstants

OfferType = Union[str, ByteString]


class CameraStreamController:

    async def get_webrtc_answer(self, jsn, get_webrtc_answer_callback: Callable[[str, OfferType], tuple[bool, Optional[bytes]]]) -> tuple[bool, Optional[bytes]]:
        self.offer: OfferType = jsn.get("payload").get("value").get("offer")

        return get_webrtc_answer_callback(jsn.get("payload").get(SinricProConstants.DEVICEID),
                                          self.offer)

    async def get_camera_stream_url(self, jsn: Any, get_camera_stream_url_callback: Callable[[str, str], tuple[bool, str]]) -> tuple[bool, str]:
        self.protocol = jsn.get("payload").get("value").get("protocol")

        return get_camera_stream_url_callback(jsn.get("payload").get(SinricProConstants.DEVICEID),
                                              self.protocol)
