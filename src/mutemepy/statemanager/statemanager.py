import logging
from typing import Callable

from .states import Idle, LongTap, MultiTapDetect, StartTap, State, TapEnd

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class StateManager:
    def __init__(self, long_tap_delay: int, multi_tap_delay: int) -> None:
        self.long_tap_delay: int = long_tap_delay
        self.multi_tap_delay: int = multi_tap_delay

        self.idle_state: State = Idle()
        self.start_tap_state: State = StartTap()
        self.tap_end_state: State = TapEnd()
        self.multi_tap_detect_state: State = MultiTapDetect()
        self.long_tap_state: State = LongTap()

        self._current_state: State = self.idle_state

    def setState(self, state: State) -> None:
        self._current_state = state

    def on_data(self, notify_func: Callable[[str, int], None], data: int) -> None:
        self._current_state.on_data(self, notify_func, data)

    def on_tick(self, notify_func: Callable[[str, int], None]) -> None:
        self._current_state.on_tick(self, notify_func)
