import logging
from typing import Callable
from .states import State
from .states import Idle, StartTap, TapEnd, MultiTapDetect, LongTap

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class StateManager:
    def __init__(self, long_tap_delay, multi_tap_delay):
        self.long_tap_delay = long_tap_delay
        self.multi_tap_delay = multi_tap_delay

        self.idle_state = Idle()
        self.start_tap_state = StartTap()
        self.tap_end_state = TapEnd()
        self.multi_tap_detect_state = MultiTapDetect()
        self.long_tap_state = LongTap()

        self._current_state = self.idle_state

    def setState(self, state: State):
        self._current_state = state

    def on_data(self, notify_func: Callable[[str, int], None], data: int):
        self._current_state.on_data(self, notify_func, data)

    def on_tick(self, notify_func: Callable[[str, int], None]):
        self._current_state.on_tick(self, notify_func)
