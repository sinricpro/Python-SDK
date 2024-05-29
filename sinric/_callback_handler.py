"""
 *  Copyright (c) 2019-2023 Sinric. All rights reserved.
 *  Licensed under Creative Commons Attribution-Share Alike (CC BY-SA)
 *
 *  This file is part of the Sinric Pro (https://github.com/sinricpro/)
"""

from collections.abc import Callable
import hmac as sinricHmac
from json import dumps
from re import X
from time import time
from typing import Any, Final, NoReturn, Optional
from uuid import uuid4

import loguru
from websockets import client

from ._brightness_controller import BrightnessController
from ._camera_stream_controller import CameraStreamController
from ._color_controller import ColorController
from ._color_temperature import ColorTemperatureController
from ._leaky_bucket import LeakyBucket
from ._lock_controller import LockStateController
from ._mode_controller import ModeController
from ._power_controller import PowerController
from ._power_level_controller import PowerLevelController
from ._range_value_controller import RangeValueController
from ._signature import Signature
from ._sinricpro_constants import SinricProConstants
from ._speaker_controller import SpeakerController
from ._temperature_controller import TemperatureController
from ._thermostat_controller import ThermostateMode
from ._tv_contorller import TvController
from ._types import SinricProTypes

# noinspection PyBroadException


class CallBackHandler(PowerLevelController, PowerController, BrightnessController, ColorController, ColorTemperatureController,
                      ThermostateMode, RangeValueController, TemperatureController, TvController, SpeakerController,
                      LockStateController, ModeController, CameraStreamController, Signature):
    def __init__(self, callbacks: SinricProTypes.RequestCallbacks, trace_bool: bool, logger: loguru.Logger, enable_track: bool = False, secret_key: str = ""):
        self.myHmac: Optional[sinricHmac.HMAC] = None
        self.secret_key: Final[str] = secret_key
        self.bucket: Final[LeakyBucket] = LeakyBucket(10, 1000, 60000)
        self.enable_track: bool = enable_track

        PowerLevelController.__init__(self, 0)
        BrightnessController.__init__(self, 0)
        PowerController.__init__(self)
        RangeValueController.__init__(self, 0)
        ColorController.__init__(self)
        ThermostateMode.__init__(self)
        TemperatureController.__init__(self, 0)
        TvController.__init__(self, 0)
        LockStateController.__init__(self)
        Signature.__init__(self, self.secret_key)
        SpeakerController.__init__(self)
        ModeController.__init__(self)
        ColorTemperatureController.__init__(
            self, 0, [2200, 2700, 4000, 5500, 7000])
        CameraStreamController.__init__(self)

        self.callbacks: SinricProTypes.RequestCallbacks = callbacks
        self.logger: loguru.Logger = logger
        self.trace_response: bool = trace_bool

    async def handle_callbacks(self, data_array: list[Any], connection: client.Connect, udp_client):
        jsn = data_array[0]
        response_cmd = data_array[1]
        message_type = data_array[2]
        # TODO check this in python39
        handleResponseType: Callable[[dict, client.Connect, Any], NoReturn]

        async def handle_response(response: dict, connection: client.Connect, udp_client) -> NoReturn:
            # TODO What are types for connection and udp clinet?
            if self.trace_response:
                self.logger.info(f"Response : {dumps(response)}")
            if response_cmd == 'socket_response':
                await connection.send(dumps(response))
            elif response_cmd == 'udp_response' and udp_client != None:
                udp_client.sendResponse(
                    dumps(response).encode('ascii'), data_array[2])

        def json_response(action: SinricProConstants, resp: bool, data_dict: dict[str, Any], instance_id='') -> dict:
            # TODO Define a json response type
            header = {
                "payloadVersion": 2,
                "signatureVersion": 1
            }
            payload = {
                "action": action,
                "clientId": jsn.get("payload").get("clientId", "alexa-skill"),
                "createdAt": int(time()),
                "deviceId": jsn.get("payload").get("deviceId", ""),
                "message": "OK",
                "replyToken": jsn.get("payload", "").get("replyToken", str(uuid4())),
                "success": resp,
                "type": "response",
                "value": data_dict
            }

            if instance_id:
                payload['instanceId'] = instance_id

            signature = self.get_signature(payload)

            return {"header": header, "payload": payload, "signature": signature}

        if message_type == 'request_response':
            assert (self.verify_signature(jsn.get('payload'),
                    jsn.get("signature").get("HMAC")))
            action = jsn.get('payload').get('action')

            if action == SinricProConstants.SET_POWER_STATE:
                await self._handle_set_power_state(connection, udp_client, jsn, handle_response, json_response, action)

            elif action == SinricProConstants.SET_POWER_LEVEL:
                await self._handle_set_power_level(connection, udp_client, jsn, handle_response, json_response, action)

            elif action == SinricProConstants.ADJUST_POWER_LEVEL:
                await self._handle_adjust_power_level(connection, udp_client, jsn, handle_response, json_response, action)

            elif action == SinricProConstants.SET_BRIGHTNESS:
                await self._handle_set_brightness(connection, udp_client, jsn, handle_response, json_response, action)

            elif action == SinricProConstants.ADJUST_BRIGHTNESS:
                await self._handle_adjust_brightness(connection, udp_client, jsn, handle_response, json_response, action)

            elif action == SinricProConstants.SET_COLOR:
                await self._handle_set_color(connection, udp_client, jsn, handle_response, json_response, action)

            elif action == SinricProConstants.SET_COLOR_TEMPERATURE:
                await self._handle_set_color_tempreature(connection, udp_client, jsn, handle_response, json_response, action)

            elif action == SinricProConstants.INCREASE_COLOR_TEMPERATURE:
                await self._handle_increase_color_tempreature(connection, udp_client, jsn, handle_response, json_response, action)

            elif action == SinricProConstants.DECREASE_COLOR_TEMPERATURE:
                await self._handle_decrease_color_tempreature(connection, udp_client, jsn, handle_response, json_response, action)

            elif action == SinricProConstants.SET_THERMOSTAT_MODE:
                await self._handle_set_thermostat_mode(connection, udp_client, jsn, handle_response, json_response, action)

            elif action == SinricProConstants.SET_RANGE_VALUE:
                await self._handle_set_range_value(connection, udp_client, jsn, handle_response, json_response, action)

            elif action == SinricProConstants.ADJUST_RANGE_VALUE:
                await self._handle_adjust_range_value(connection, udp_client, jsn, handle_response, json_response, action)

            elif action == SinricProConstants.TARGET_TEMPERATURE:
                await self._handle_target_tempreature(connection, udp_client, jsn, handle_response, json_response, action)

            elif action == SinricProConstants.ADJUST_TARGET_TEMPERATURE:
                await self._handle_adjust_target_tempreature(connection, udp_client, jsn, handle_response, json_response, action)

            elif action == SinricProConstants.SET_VOLUME:
                await self._handle_set_volume(connection, udp_client, jsn, handle_response, json_response, action)

            elif action == SinricProConstants.ADJUST_VOLUME:
                await self._handle_adjust_volume(connection, udp_client, jsn, handle_response, json_response, action)

            elif action == SinricProConstants.MEDIA_CONTROL:
                await self._handle_media_control(connection, udp_client, jsn, handle_response, json_response, action)

            elif action == SinricProConstants.SELECT_INPUT:
                await self._handle_select_input(connection, udp_client, jsn, handle_response, json_response, action)

            elif action == SinricProConstants.CHANGE_CHANNEL:
                await self._handle_change_channel(connection, udp_client, jsn, handle_response, json_response, action)

            elif action == SinricProConstants.SKIP_CHANNELS:
                await self._handle_skip_channel(connection, udp_client, jsn, handle_response, json_response, action)

            elif action == SinricProConstants.SET_MUTE:
                await self._handle_set_mute(connection, udp_client, jsn, handle_response, json_response, action)

            elif action == SinricProConstants.SET_BANDS:
                await self._handle_set_bands(connection, udp_client, jsn, handle_response, json_response, action)

            elif action == SinricProConstants.ADJUST_BANDS:
                await self._handle_adjust_bands(connection, udp_client, jsn, handle_response, json_response, action)

            elif action == SinricProConstants.RESET_BANDS:
                await self._handle_reset_bands(connection, udp_client, jsn, handle_response, json_response, action)

            elif action == SinricProConstants.SET_MODE:
                await self._handle_set_mode(connection, udp_client, jsn, handle_response, json_response, action)

            elif action == SinricProConstants.SET_LOCK_STATE:
                await self._handle_set_lock_state(connection, udp_client, jsn, handle_response, json_response, action)

            elif action == SinricProConstants.GET_WEBRTC_ANSWER:
                await self._handle_get_webrtc_answer(connection, udp_client, jsn, handle_response, json_response, action)

            elif action == SinricProConstants.GET_CAMERA_STREAM_URL:
                await self._handle_get_camera_stream_url(connection, udp_client, jsn, handle_response, json_response, action)

        # Handle events

        if message_type == 'event':
            if response_cmd == SinricProConstants.DOORBELLPRESS:
                if self.bucket.add_drop():
                    self.logger.info('Sending Doorbell event')
                    await connection.send(dumps(jsn))

            elif response_cmd == SinricProConstants.CURRENT_TEMPERATURE:
                if self.bucket.add_drop():
                    self.logger.info('Sending temperature humidity event')
                    await connection.send(dumps(jsn))

            elif response_cmd == SinricProConstants.SET_POWER_STATE:
                if self.bucket.add_drop():
                    self.logger.info('Sending power state event')
                    await connection.send(dumps(jsn))

            elif response_cmd == SinricProConstants.SET_POWER_LEVEL:
                if self.bucket.add_drop():
                    self.logger.info('Sending power level event')
                    await connection.send(dumps(jsn))

            elif response_cmd == SinricProConstants.SET_BRIGHTNESS:
                if self.bucket.add_drop():
                    self.logger.info('Sending brightness event')
                    await connection.send(dumps(jsn))

            elif response_cmd == SinricProConstants.SET_COLOR:
                if self.bucket.add_drop():
                    self.logger.info('Sending color event')
                    await connection.send(dumps(jsn))

            elif response_cmd == SinricProConstants.SET_COLOR_TEMPERATURE:
                if self.bucket.add_drop():
                    self.logger.info('Sending color temperature event')
                    await connection.send(dumps(jsn))

            elif response_cmd == SinricProConstants.SET_THERMOSTAT_MODE:
                if self.bucket.add_drop():
                    self.logger.info('Sending thermostat mode event')
                    await connection.send(dumps(jsn))

            elif response_cmd == SinricProConstants.SET_RANGE_VALUE:
                if self.bucket.add_drop():
                    self.logger.info('Sending range value event')
                    await connection.send(dumps(jsn))

            elif response_cmd == SinricProConstants.MOTION:
                if self.bucket.add_drop():
                    self.logger.info('Sending motion event')
                    await connection.send(dumps(jsn))

            elif response_cmd == SinricProConstants.SET_CONTACT_STATE:
                if self.bucket.add_drop():
                    self.logger.info('Sending contact event')
                    await connection.send(dumps(jsn))

            elif response_cmd == SinricProConstants.SET_VOLUME:
                if self.bucket.add_drop():
                    self.logger.info('Sending voluming event')
                    await connection.send(dumps(jsn))

            elif response_cmd == SinricProConstants.SELECT_INPUT:
                if self.bucket.add_drop():
                    self.logger.info('Sending select input event')
                    await connection.send(dumps(jsn))

            elif response_cmd == SinricProConstants.MEDIA_CONTROL:
                if self.bucket.add_drop():
                    self.logger.info('Sending media control event')
                    await connection.send(dumps(jsn))

            elif response_cmd == SinricProConstants.CHANGE_CHANNEL:
                if self.bucket.add_drop():
                    self.logger.info('Sending change channel event')
                    await connection.send(dumps(jsn))

            elif response_cmd == SinricProConstants.SET_BANDS:
                if self.bucket.add_drop():
                    self.logger.info('Sending band event')
                    await connection.send(dumps(jsn))

            elif response_cmd == SinricProConstants.SET_MODE:
                if self.bucket.add_drop():
                    self.logger.info('Sending mode event')
                    await connection.send(dumps(jsn))

            elif response_cmd == SinricProConstants.SET_LOCK_STATE:
                if self.bucket.add_drop():
                    self.logger.info('Sending lock event')
                    await connection.send(dumps(jsn))

            elif response_cmd == SinricProConstants.RESET_BANDS:
                if self.bucket.add_drop():
                    self.logger.info('Sending reset bands event')
                    await connection.send(dumps(jsn))

            elif response_cmd == SinricProConstants.PUSH_NOTIFICATION:
                if self.bucket.add_drop():
                    self.logger.info('Sending push notification event')
                    await connection.send(dumps(jsn))

    async def _handle_get_camera_stream_url(self, connection, udp_client, jsn, handle_response, json_response, action):
        try:
            resp, url = await self.get_camera_stream_url(jsn, self.callbacks.get(action))
            response = json_response(action, resp, {"url": url})

            if resp:
                await handle_response(response, connection, udp_client)
        except AssertionError:
            self.logger.error(
                "Signature verification failed for " + jsn.get('payload').get('action'))
        except Exception as e:
            self.logger.error(str(e))

    async def _handle_get_webrtc_answer(self, connection, udp_client, jsn, handle_response, json_response, action):
        try:
            resp, value = await self.get_webrtc_answer(jsn, self.callbacks.get(action))
            response = json_response(action, resp, {"answer": value})

            if resp:
                await handle_response(response, connection, udp_client)
        except AssertionError:
            self.logger.error(
                "Signature verification failed for " + jsn.get('payload').get('action'))
        except Exception as e:
            self.logger.error(str(e))

    async def _handle_set_lock_state(self, connection, udp_client, jsn, handle_response, json_response, action):
        try:
            resp, value = await self.set_lock_state(jsn, self.callbacks.get(action))
            # TODO: Fix this later
            response = json_response(
                action, resp, {"state": value.upper() + 'ED'})

            if resp:
                await handle_response(response, connection, udp_client)
        except AssertionError:
            self.logger.error(
                "Signature verification failed for " + jsn.get('payload').get('action'))
        except Exception as e:
            self.logger.error(str(e))

    async def _handle_set_mode(self, connection, udp_client, jsn, handle_response, json_response, action):
        try:
            resp, value, instance_id = await self.set_mode(jsn, self.callbacks.get(action))
            response = json_response(action, resp, {
                "mode": value
            }, instance_id)

            if resp:
                await handle_response(response, connection, udp_client)
        except AssertionError:
            self.logger.error(
                "Signature verification failed for " + jsn.get('payload').get('action'))
        except Exception as e:
            self.logger.error(str(e))

    async def _handle_reset_bands(self, connection, udp_client, jsn, handle_response, json_response, action):
        try:
            resp = await self.reset_bands(jsn, self.callbacks.get(action))
            response = json_response(action, resp, {
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
            if resp:
                await handle_response(response, connection, udp_client)
        except AssertionError:
            self.logger.error(
                "Signature verification failed for " + jsn.get('payload').get('action'))
        except Exception as e:
            self.logger.error(str(e))

    async def _handle_adjust_bands(self, connection, udp_client, jsn, handle_response, json_response, action):
        try:
            resp, value = await self.adjust_bands(jsn, self.callbacks.get(action))
            response = json_response(action, resp, {
                "bands": [
                    {
                        "name": value.get('name'),
                        "level": value.get('level')
                    }
                ]
            })

            if resp:
                await handle_response(response, connection, udp_client)
        except AssertionError:
            self.logger.error(
                "Signature verification failed for " + jsn.get('payload').get('action'))
        except Exception as e:
            self.logger.error(str(e))

    async def _handle_set_bands(self, connection, udp_client, jsn, handle_response, json_response, action):
        try:
            resp, value = await self.set_bands(jsn, self.callbacks.get(action))
            response = json_response(action, resp, {
                "bands": [
                    {
                        "name": value.get('name'),
                        "level": value.get('level')
                    }
                ]
            })

            if resp:
                await handle_response(response, connection, udp_client)
        except AssertionError:
            self.logger.error(
                "Signature verification failed for " + jsn.get('payload').get('action'))
        except Exception as e:
            self.logger.error(str(e))

    async def _handle_set_mute(self, connection, udp_client, jsn, handle_response, json_response, action):
        try:
            resp, value = await self.set_mute(jsn, self.callbacks.get(action))
            response = json_response(action, resp, {"mute": value})

            if resp:
                await handle_response(response, connection, udp_client)
        except AssertionError:
            self.logger.error(
                "Signature verification failed for " + jsn.get('payload').get('action'))
        except Exception as e:
            self.logger.error(str(e))

    async def handle_skip_channel(self, connection, udp_client, jsn, handle_response, json_response, action):
        try:
            resp, value = await self.skip_channels(jsn, self.callbacks.get(action))
            response = json_response(
                action, resp, {"channel": {"name": value}})

            if resp:
                await handle_response(response, connection, udp_client)
        except AssertionError:
            self.logger.error(
                "Signature verification failed for " + jsn.get('payload').get('action'))
        except Exception as e:
            self.logger.error(str(e))

    async def _handle_change_channel(self, connection, udp_client, jsn, handle_response, json_response, action):
        try:
            resp, value = await self.change_channel(jsn, self.callbacks.get(action))
            response = json_response(
                action, resp, {"channel": {"name": value}})
            if resp:
                await handle_response(response, connection, udp_client)
        except AssertionError:
            self.logger.error(
                "Signature verification failed for " + jsn.get('payload').get('action'))
        except Exception as e:
            self.logger.error(str(e))

    async def _handle_select_input(self, connection, udp_client, jsn, handle_response, json_response, action):
        try:
            resp, value = await self.select_input(jsn, self.callbacks.get(action))
            response = json_response(action, resp, {"input": value})
            if resp:
                await handle_response(response, connection, udp_client)
        except AssertionError:
            self.logger.error(
                "Signature verification failed for " + jsn.get('payload').get('action'))
        except Exception as e:
            self.logger.error(str(e))

    async def _handle_media_control(self, connection, udp_client, jsn, handle_response, json_response, action):
        try:
            resp, value = await self.media_control(jsn, self.callbacks.get(action))
            response = json_response(action, resp, {"control": value})
            if resp:
                await handle_response(response, connection, udp_client)
        except AssertionError:
            self.logger.error(
                "Signature verification failed for " + jsn.get('payload').get('action'))
        except Exception as e:
            self.logger.error(str(e))

    async def _handle_adjust_volume(self, connection, udp_client, jsn, handle_response, json_response, action):
        try:
            resp, value = await self.adjust_volume(jsn, self.callbacks.get(action))
            response = json_response(action, resp, {"volume": value})

            if resp:
                await handle_response(response, connection, udp_client)
        except AssertionError:
            self.logger.error(
                "Signature verification failed for " + jsn.get('payload').get('action'))
        except Exception as e:
            self.logger.error(str(e))

    async def _handle_set_volume(self, connection, udp_client, jsn, handle_response, json_response, action):
        try:
            resp, value = await self.set_volume(jsn, self.callbacks.get(action))
            response = json_response(action, resp, {"volume": value})

            if resp:
                await handle_response(response, connection, udp_client)
        except AssertionError:
            self.logger.error(
                "Signature verification failed for " + jsn.get('payload').get('action'))
        except Exception as e:
            self.logger.error(str(e))

    async def _handle_adjust_target_tempreature(self, connection, udp_client, jsn, handle_response, json_response, action):
        try:
            resp, value = await self.adjust_temperature(jsn, self.callbacks.get(action))
            response = json_response(action, resp, {"temperature": value})
            if resp:
                await handle_response(response, connection, udp_client)
        except AssertionError:
            self.logger.error(
                "Signature verification failed for " + jsn.get('payload').get('action'))
        except Exception as e:
            self.logger.error(str(e))

    async def _handle_target_tempreature(self, connection, udp_client, jsn, handle_response, json_response, action):
        try:
            resp, value = await self.target_temperature(jsn, self.callbacks.get(action))
            response = json_response(action, resp, {"temperature": value})

            if resp:
                await handle_response(response, connection, udp_client)
        except AssertionError:
            self.logger.error(
                "Signature verification failed for " + jsn.get('payload').get('action'))
        except Exception as e:
            self.logger.error(str(e))

    async def _handle_adjust_range_value(self, connection, udp_client, jsn, handle_response, json_response, action):
        try:
            resp, value = await self.adjust_range_value(jsn, self.callbacks.get('adjustRangeValue'))
            response = json_response(action, resp, {"rangeValue": value})
            if resp:
                await handle_response(response, connection, udp_client)
        except AssertionError:
            self.logger.error(
                "Signature verification failed for " + jsn.get('payload').get('action'))
        except Exception as e:
            self.logger.error(str(e))

    async def _handle_set_range_value(self, connection, udp_client, jsn, handle_response, json_response, action):
        try:
            resp, value, instance_id = await self.set_range_value(jsn, self.callbacks.get(action))
            response = json_response(
                action, resp, {"rangeValue": value}, instance_id)
            if resp:
                await handle_response(response, connection, udp_client)
        except AssertionError:
            self.logger.error(
                "Signature verification failed for " + jsn.get('payload').get('action'))
        except Exception as e:
            self.logger.error(str(e))

    async def _handle_set_thermostat_mode(self, connection, udp_client, jsn, handle_response, json_response, action):
        try:
            resp, value = await self.set_thermostate_mode(jsn, self.callbacks[action])
            response = json_response(action, resp, {"thermostatMode": value})

            if resp:
                await handle_response(response, connection, udp_client)
        except Exception as e:
            self.logger.error(f'Error : {e}')

    async def _handle_decrease_color_tempreature(self, connection, udp_client, jsn, handle_response, json_response, action):
        try:
            resp, value = await self.decrease_color_temperature(jsn, self.callbacks[action])
            response = json_response(action, resp, {"colorTemperature": value})

            if resp:
                await handle_response(response, connection, udp_client)
        except AssertionError:
            self.logger.error(
                "Signature verification failed for " + jsn.get('payload').get('action'))
        except Exception as e:
            self.logger.error(f'Error : {e}')

    async def _handle_increase_color_tempreature(self, connection, udp_client, jsn, handle_response, json_response, action):
        try:
            resp, value = await self.increase_color_temperature(jsn, self.callbacks[action])
            response = json_response(action, resp, {"colorTemperature": value})

            if resp:
                await handle_response(response, connection, udp_client)
        except AssertionError:
            self.logger.error(
                "Signature verification failed for " + jsn.get('payload').get('action'))
        except Exception as e:
            self.logger.error(f'Error : {e}')

    async def _handle_set_color_tempreature(self, connection, udp_client, jsn, handle_response, json_response, action):
        try:
            resp = await self.set_color_temperature(jsn, self.callbacks[action])
            response = json_response(action, resp, {"colorTemperature": jsn.get(
                "payload").get("value").get("colorTemperature")})

            if resp:
                await handle_response(response, connection, udp_client)
        except AssertionError:
            self.logger.error(
                "Signature verification failed for " + jsn.get('payload').get('action'))
        except Exception as e:
            self.logger.error(f'Error : {e}')

    async def _handle_set_color(self, connection, udp_client, jsn, handle_response, json_response, action):
        try:
            resp = await self.set_color(jsn, self.callbacks[action])
            response = json_response(action=action, resp=resp, data_dict={
                "color": {
                    "b": jsn.get("payload").get("value").get("color").get("b"),
                    "g": jsn.get("payload").get("value").get("color").get("g"),
                    "r": jsn.get("payload").get("value").get("color").get("r")
                }
            })

            if resp:
                await handle_response(response, connection, udp_client)
        except AssertionError:
            self.logger.error(
                "Signature verification failed for " + jsn.get('payload').get('action'))
        except Exception as e:
            self.logger.error(f'Error : {e}')

    async def _handle_adjust_brightness(self, connection, udp_client, jsn, handle_response, json_response, action):
        try:
            resp, value = await self.adjust_brightness(jsn, self.callbacks[action])
            response = json_response(action, resp, {"brightness": value})

            if resp:
                await handle_response(response, connection, udp_client)
        except AssertionError:
            self.logger.error(
                "Signature verification failed for " + jsn.get('payload').get('action'))
        except Exception as e:
            self.logger.error(f'Error : {e}')

    async def _handle_set_brightness(self, connection, udp_client, jsn, handle_response, json_response, action):
        try:
            resp, value = await self.set_brightness(jsn, self.callbacks[action])
            response = json_response(action, resp, {"brightness": value})

            if resp:
                await handle_response(response, connection, udp_client)
        except AssertionError:
            self.logger.error(
                "Signature verification failed for " + jsn.get('payload').get('action'))
        except Exception as e:
            self.logger.error(f'Error : {e}')

    async def _handle_adjust_power_level(self, connection, udp_client, jsn, handle_response, json_response, action):
        try:
            resp, value = await self.adjust_power_level(jsn, self.callbacks[action])
            response = json_response(action, resp, {"powerLevel": value})

            if resp:
                await handle_response(response, connection, udp_client)
        except AssertionError:
            self.logger.error(
                "Signature verification failed for " + jsn.get('payload').get('action'))
        except Exception as e:
            self.logger.error(f'Error : {e}')

    async def _handle_set_power_level(self, connection, udp_client, jsn, handle_response, json_response, action):
        try:
            resp, value = await self.set_power_level(jsn, self.callbacks[action])
            response = json_response(action, resp, {"powerLevel": value})

            if resp:
                await handle_response(response, connection, udp_client)
        except AssertionError:
            self.logger.error(
                "Signature verification failed for " + jsn.get('payload').get('action'))
        except Exception as e:
            self.logger.error(str(e))

    async def _handle_set_power_state(self, connection, udp_client, jsn, handle_response, json_response, action):
        try:
            resp, state = await self.power_state(jsn, self.callbacks[action])
            response = json_response(action, resp, {"state": state})
            if resp:
                await handle_response(response, connection, udp_client)
        except AssertionError:
            self.logger.error(
                "Signature verification failed for " + jsn.get('payload').get('action'))
        except Exception as e:
            self.logger.error(f'Error : {e}')

        # else:
        #    self.logger.info(response_cmd + ' not found!')
