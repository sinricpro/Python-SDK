from collections.abc import Callable
from typing import ByteString, Final, Optional, Union
from sinric import SinricPro, SinricProConstants
import requests
import asyncio
import base64

APP_KEY: Final[str] = ''
APP_SECRET: Final[str] = ''
CAMERA_ID: Final[str] = ''

OfferType = Union[str, ByteString]

CallbackFunctions = Union[
    Callable[[str, str], tuple[bool, str]],  # Power state / Camera Stream Url
    Callable[[str, OfferType], tuple[bool, Optional[bytes]]],  # WEBRTC Answer

]


def get_webrtc_answer(device_id: str, offer: OfferType) -> tuple[bool, Optional[bytes]]:
    sdp_offer: Final[bytes] = base64.b64decode(offer)
    print('device_id: {} offer: {}'.format(device_id, offer))

    # PORT 8889 for WebRTC. eg: for PiCam, use http://<mediamtx-hostname>:8889/cam/whep
    mediamtx_url: Final[str] = "http://<mediamtx-hostname>:8889/<device>/whep"
    headers: dict[str, str] = {"Content-Type": "application/sdp"}
    response: requests.Response = requests.post(
        mediamtx_url, headers=headers, data=sdp_offer)

    if response.status_code == 201:
        answer: bytes = base64.b64encode(response.content).decode("utf-8")
        return True, answer
    else:
        return False, None


def power_state(device_id: str, state: str) -> tuple[bool, str]:
    print('device_id: {} power state: {}'.format(device_id, state))
    return True, state


def get_camera_stream_url(device_id: str, protocol: str) -> tuple[bool, str]:
    # TODO: Should protocol be a string literal?
    # Google Home: RTSP protocol not supported. Requires a Chromecast TV or Google Nest Hub
    # Alexa: RTSP url must be interleaved TCP on port 443 (for both RTP and RTSP) over TLS 1.2 port 443

    print('device_id: {} protocol: {}'.format(device_id, protocol))

    if protocol == "rstp":
        return True, 'rtsp://rtspurl:443'   # RSTP.
    else:
        return True, 'https://cph-p2p-msl.akamaized.net/hls/live/2000341/test/master.m3u8'  # HLS


callbacks: dict[str, CallbackFunctions] = {
    SinricProConstants.GET_WEBRTC_ANSWER: get_webrtc_answer,
    SinricProConstants.GET_CAMERA_STREAM_URL: get_camera_stream_url,
    SinricProConstants.SET_POWER_STATE: power_state
}

if __name__ == '__main__':
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    client: SinricPro = SinricPro(APP_KEY, [CAMERA_ID], callbacks,
                                  enable_log=False, restore_states=False, secret_key=APP_SECRET)
    loop.run_until_complete(client.connect())
