from collections.abc import Callable
from numbers import Real
from typing import Union


class SinricProTypes(object):
    RequestCallbacks = dict[str, Callable]
    EventCallbacks = Callable[[]]

    BandDictType = dict[str, Union[str, Real]]
