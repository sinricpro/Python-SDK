import time
from typing import Final


class LeakyBucket:
    def __init__(self, bucket_size: int, drop_in_time: int, drop_out_time: int):
        self.bucket_size: Final[int] = bucket_size
        self.drop_in_time: int = drop_in_time
        self.drop_out_time: int = drop_out_time
        self.drop_in_bucket: int = 0
        self.last_drop: int = 0

    def millis(self) -> int:
        return int(round(time.time() * 1000))

    def leak_drops(self) -> None:
        actual_millis: int = self.millis()
        drops_to_leak: int = round(
            (actual_millis - self.last_drop) / self.drop_out_time)
        if drops_to_leak > 0:
            if self.drop_in_bucket <= drops_to_leak:
                self.drop_in_bucket = 0
            else:
                self.drop_in_bucket = self.drop_in_bucket - drops_to_leak

    def add_drop(self) -> bool:
        self.leak_drops()
        actual_millis: int = self.millis()
        if (self.drop_in_bucket < self.bucket_size) and (
                (actual_millis - self.last_drop) > (self.drop_in_bucket + self.drop_in_time)):
            self.drop_in_bucket = self.drop_in_bucket + 1
            self.last_drop = actual_millis
            return True
        if self.drop_in_bucket >= self.bucket_size:
            return False
        return False
