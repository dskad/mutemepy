import logging
from typing import Callable
from .states import State
from .states import Idle, StartTap, TapEnd, MultiTapDetect, LongTap

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class StateManager:
    def __init__(self, long_tap_delay, multi_tap_delay):
        self._long_tap_delay = long_tap_delay
        self._multi_tap_delay = multi_tap_delay
        self._idle_state = Idle()
        self._start_tap_state = StartTap()
        self._tap_end_state = TapEnd()
        self._multi_tap_detect_state = MultiTapDetect()
        self._long_tap_state = LongTap()

        self._state = self._idle_state

    # Property use here is to make attributes read only. This helps prevent difficult to find
    # bugs when a state accidentally is overwritten with another state
    @property
    def idle_state(self):
        return self._idle_state

    @property
    def start_tap_state(self):
        return self._start_tap_state

    @property
    def tap_end_state(self):
        return self._tap_end_state

    @property
    def long_tap_state(self):
        return self._long_tap_state

    @property
    def multi_tap_detect_state(self):
        return self._multi_tap_detect_state

    def setState(self, state: State):
        # log.debug(f"Setting state to {self._state}")
        self._state = state

    def on_data(self, notify_func: Callable[[str, int], None], data: int):
        self._state.on_data(self, notify_func, data)

    def on_tick(self, notify_func: Callable[[str, int], None]):
        self._state.on_tick(self, notify_func)
