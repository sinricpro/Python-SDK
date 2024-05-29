from json import dumps
from base64 import b64encode
import hmac as sinricHmac
from hashlib import sha256
from typing import Final, Optional


class Signature:
    def __init__(self, secret_key: str):
        self.secret_key: str = secret_key
        self.hmac: Optional[sinricHmac.HMAC] = None

    def verify_signature(self, payload, signature: str) -> bool:
        self.hmac = sinricHmac.new(self.secret_key.encode('utf-8'),
                                   dumps(payload, separators=(',', ':')).encode('utf-8'), sha256)
        return b64encode(self.hmac.digest()).decode('utf-8') == signature

    def get_signature(self, payload) -> dict[str, str]:
        # TODO is there a special type for json payload?
        reply_hmac: sinricHmac.HMAC = sinricHmac.new(self.secret_key.encode('utf-8'),
                                                     dumps(payload, separators=(',', ':')).encode('utf-8'), sha256)

        encoded_hmac: bytes = b64encode(reply_hmac.digest())

        return {
            "HMAC": encoded_hmac.decode('utf-8')
        }
