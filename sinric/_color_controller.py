"""
 *  Copyright (c) 2019-2023 Sinric. All rights reserved.
 *  Licensed under Creative Commons Attribution-Share Alike (CC BY-SA)
 *
 *  This file is part of the Sinric Pro (https://github.com/sinricpro/)
"""


from collections.abc import Callable


class ColorController:

    async def set_color(self, jsn, set_color_callback: Callable[[str, int, int, int], bool]) -> bool:
        return set_color_callback(jsn.get("payload").get("deviceId"),
                                  jsn.get("payload").get(
                                      "value").get("color").get("r"),
                                  jsn.get("payload").get(
                                      "value").get("color").get("g"),
                                  jsn.get("payload").get("value").get("color").get("b"))
