"""
 *  Copyright (c) 2019-2023 Sinric. All rights reserved.
 *  Licensed under Creative Commons Attribution-Share Alike (CC BY-SA)
 *
 *  This file is part of the Sinric Pro (https://github.com/sinricpro/)
"""

import asyncio
import json
from time import time
from typing import Final, NoReturn, Optional
from loguru import Logger

import pkg_resources
from websockets import client
from websockets.exceptions import ConnectionClosed

from ._callback_handler import CallBackHandler
from ._queues import queue
from ._signature import Signature
from ._types import SinricProTypes
from .helpers.wait import waitAsync


class SinricProSocket(Signature):

    def __init__(self, app_key: str, device_id: str, callbacks: SinricProTypes.RequestCallbacks,
                 enable_trace: bool = False, logger: Logger = None, restore_states: bool = False,
                 secret_key: str = "", loop_delay: float = 0.5):
        self.app_key: Final[str] = app_key
        self.secret_key: Final[str] = secret_key
        self.restore_states: Final[bool] = restore_states
        self.logger: Final[Logger] = logger
        self.device_ids: Final[list[str]] = device_id
        self.connection: Optional[client.Connect] = None
        self.callbacks: SinricProTypes.RequestCallbacks = callbacks
        self.loop_delay: Final[float] = loop_delay

        self.callbackHandler: CallBackHandler = CallBackHandler(self.callbacks, enable_trace, self.logger, self.restore_states,
                                                                secret_key=self.secret_key)
        self.enableTrace: Final[bool] = enable_trace
        Signature.__init__(self, self.secret_key)

    async def connect(self) -> client.Connect:  # Producer
        sdk_version = pkg_resources.require("sinricpro")[0].version
        self.connection: client.Connect = await client.connect('wss://ws.sinric.pro',
                                                               extra_headers={'appkey': self.app_key,
                                                                              'deviceids': ';'.join(self.device_ids),
                                                                              'platform': 'python',
                                                                              'sdkversion': sdk_version,
                                                                              'restoredevicestates': (
                                                                                  'true' if self.restore_states else 'false')},
                                                               ping_interval=30000, ping_timeout=10000)
        if self.connection.open:
            self.logger.success("Connected :)")
            timestamp = await self.connection.recv()
            if (int(time()) - json.loads(timestamp).get('timestamp') > 60000):
                self.logger.warning(
                    'Timestamp is not in sync. Please check your system time.')
            return self.connection

    async def receive_message(self, connection: client.Connect) -> NoReturn:
        while True:
            try:
                message = await waitAsync(connection.recv())
                if message is None:
                    continue
                if self.enableTrace:
                    self.logger.info(f"Request : {message}")
                request = json.loads(message)
                queue.put([request, 'socket_response', 'request_response'])
                await asyncio.sleep(self.loop_delay)
            except ConnectionClosed as e:
                self.logger.info('Connection with server closed')
                raise e

    async def handle_queue(self) -> NoReturn:
        while True:
            await asyncio.sleep(self.loop_delay)

            while queue.qsize() > 0:
                await self.callbackHandler.handle_callbacks(queue.get(), self.connection, None)
