"""
 *  Copyright (c) 2019-2023 Sinric. All rights reserved.
 *  Licensed under Creative Commons Attribution-Share Alike (CC BY-SA)
 *
 *  This file is part of the Sinric Pro (https://github.com/sinricpro/)
"""

from re import S
from time import time, sleep
from typing import Final, Optional

from loguru import Logger
from ._queues import queue
import uuid
from ._signature import Signature
from ._sinricpro_constants import SinricProConstants

# noinspection PyBroadException


class Events(Signature):
    def __init__(self, connection, logger: Optional[Logger] = None, secret_key: str = ""):
        self.connection = connection
        self.logger: Optional[Logger] = logger
        self.secret_key: Final[str] = secret_key
        Signature.__init__(self, self.secret_key)

    # noinspection PyBroadException
    def raise_event(self, device_id: str, event_name, data=None):
        if data is None:
            data = {}
        try:
            def json_response(action, device_id, value, type_of_interaction="PHYSICAL_INTERACTION") -> dict:
                header = {
                    "payloadVersion": 2,
                    "signatureVersion": 1
                }

                payload = {
                    "action": action,
                    "cause": {
                        "type": type_of_interaction
                    },
                    "createdAt": int(time()),
                    "deviceId": device_id,
                    "replyToken": str(uuid.uuid4()),
                    "type": "event",
                    "value": value
                }

                signature = self.get_signature(payload)
                return {"header": header, "payload": payload, "signature": signature}

            if event_name == SinricProConstants.SET_POWER_STATE:
                response = json_response(event_name, device_id, {
                                         SinricProConstants.STATE: data.get("state", "Off")})
                queue.put([response, event_name, 'event'])

            elif event_name == SinricProConstants.SET_POWER_LEVEL:
                response = json_response(event_name, device_id, {
                                         SinricProConstants.POWER_LEVEL: data.get(SinricProConstants.POWER_LEVEL)})
                queue.put([response, event_name, 'event'])

            elif event_name == SinricProConstants.SET_BRIGHTNESS:
                response = json_response(event_name, device_id, {
                                         SinricProConstants.BRIGHTNESS: data.get(SinricProConstants.BRIGHTNESS)})
                queue.put([response, event_name, 'event'])

            elif event_name == SinricProConstants.SET_COLOR:
                response = json_response(event_name, device_id, {
                    "color": {
                        "r": data.get('r'),
                        "g": data.get('g'),
                        "b": data.get('b')
                    }
                })
                queue.put([response, event_name, 'event'])

            elif event_name == SinricProConstants.SET_COLOR_TEMPERATURE:
                response = json_response(event_name, device_id, {
                                         SinricProConstants.COLOR_TEMPERATURE: 2400})
                queue.put([response, event_name, 'event'])

            elif event_name == SinricProConstants.DOORBELLPRESS:
                response = json_response(
                    event_name, device_id, {"state": "pressed"})
                queue.put([response, event_name, 'event'])

            elif event_name == SinricProConstants.CURRENT_TEMPERATURE:
                response = json_response(event_name, device_id, {
                    SinricProConstants.TEMPERATURE: round(data.get(SinricProConstants.TEMPERATURE), 1),
                    SinricProConstants.HUMIDITY: round(data.get(SinricProConstants.HUMIDITY), 1),
                }, type_of_interaction="PERIODIC_POLL")
                queue.put([response, event_name, 'event'])

            elif event_name == SinricProConstants.PUSH_NOTIFICATION:
                response = json_response(event_name, device_id, {
                    "alert": data.get('alert'),
                })
                queue.put([response, event_name, 'event'])

            elif event_name == SinricProConstants.SET_THERMOSTAT_MODE:
                response = json_response(event_name, device_id, {
                    SinricProConstants.THERMOSTATMODE: data.get(
                        SinricProConstants.MODE)
                })
                queue.put([response, event_name, 'event'])

            elif event_name == SinricProConstants.SET_RANGE_VALUE:
                response = json_response(event_name, device_id, {
                    SinricProConstants.RANGE_VALUE: data.get(
                        SinricProConstants.RANGE_VALUE)
                })
                queue.put([response, event_name, 'event'])

            elif event_name == SinricProConstants.MOTION:
                response = json_response(SinricProConstants.MOTION, device_id, {
                    SinricProConstants.STATE: data.get(
                        SinricProConstants.STATE)
                })
                queue.put([response, event_name, 'event'])

            elif event_name == SinricProConstants.SET_CONTACT_STATE or event_name == SinricProConstants.SET_LOCK_STATE:
                response = json_response(event_name, device_id, {
                    SinricProConstants.STATE: data.get(
                        SinricProConstants.STATE)
                })
                queue.put([response, event_name, 'event'])

            elif event_name == SinricProConstants.SET_VOLUME:
                response = json_response(event_name, device_id, {
                    SinricProConstants.VOLUME: data.get(
                        SinricProConstants.VOLUME)
                })
                queue.put([response, event_name, 'event'])

            elif event_name == SinricProConstants.SELECT_INPUT:
                response = json_response(event_name, device_id, {
                    SinricProConstants.INPUT: data.get(
                        SinricProConstants.INPUT)
                })
                queue.put([response, event_name, 'event'])

            elif event_name == SinricProConstants.MEDIA_CONTROL:
                response = json_response(event_name, device_id, {
                    SinricProConstants.CONTROL: data.get(
                        SinricProConstants.CONTROL)
                })
                queue.put([response, event_name, 'event'])

            elif event_name == SinricProConstants.CHANGE_CHANNEL:
                response = json_response(event_name, device_id, {
                    "channel": {
                        "name": data.get('name')
                    }
                })
                queue.put([response, event_name, 'event'])

            elif event_name == SinricProConstants.SET_BANDS:
                response = json_response(event_name, device_id, {
                    "bands": [
                        {
                            "name": data.get('name'),
                            "level": data.get('level')
                        }
                    ]
                })
                queue.put([response, event_name, 'event'])

            elif event_name == SinricProConstants.SET_MODE:
                response = json_response(event_name, device_id, {
                    SinricProConstants.MODE: data.get(SinricProConstants.MODE)
                })
                queue.put([response, event_name, 'event'])

            elif event_name == SinricProConstants.RESET_BANDS:
                response = json_response(event_name, device_id, {
                    "bands": [
                        {
                            "name": "BASS",
                            "level": 0
                        },
                        {
                            "name": "MIDRANGE",
                            "level": 0
                        },
                        {
                            "name": "TREBLE",
                            "level": 0
                        }]
                })
                queue.put([response, event_name, 'event'])

            elif event_name == SinricProConstants.SET_MUTE:
                response = json_response(event_name, device_id, {
                    SinricProConstants.MUTE: data.get(
                        SinricProConstants.MUTE, False)
                })
                queue.put([response, event_name, 'event'])

            else:
                self.logger.exception('Event :' + event_name + ' not found!')

        except Exception:
            self.logger.exception('Error Occurred')
