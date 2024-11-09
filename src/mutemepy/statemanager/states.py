from abc import ABC, abstractmethod
import logging

from ..devicestates import TouchState
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .statemanager import StateManager

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class State(ABC):
    @abstractmethod
    def on_data(
        self, context: "StateManager", notify: Callable[[str, int], None], data: int
    ) -> None:
        pass

    def on_tick(
        self, context: "StateManager", notify: Callable[[str, int], None]
    ) -> None:
        pass


class Idle(State):
    def on_data(
        self, context: "StateManager", notify: Callable[[str, int], None], data: int
    ) -> None:
        if data == TouchState.START_TOUCH:
            context.setState(context.start_tap_state)


class StartTap(State):
    def __init__(self) -> None:
        self._timer = 0

    def on_data(
        self, context: "StateManager", notify: Callable[[str, int], None], data: int
    ) -> None:
        if data == TouchState.END_TOUCH:
            self._timer = 0
            context.setState(context.multi_tap_detect_state)

        if self._timer >= context.long_tap_delay:
            self._timer = 0
            context.setState(context.long_tap_state)
        else:
            self._timer += 1


class MultiTapDetect(State):
    def __init__(self) -> None:
        self._timer = 0
        self._multi_touch_count = 1

    def on_data(self, context: "StateManager", notify, data: int) -> None:
        if data == TouchState.START_TOUCH:
            self._timer = 0
            self._multi_touch_count += 1
            context.setState(context.start_tap_state)

    def on_tick(
        self, context: "StateManager", notify: Callable[[str, int], None]
    ) -> None:
        if self._timer >= context.multi_tap_delay:
            if self._multi_touch_count > 1:
                notify("on_multi_tap", self._multi_touch_count)
            else:
                notify("on_tap", 1)

            self._timer = 0
            self._multi_touch_count = 1
            context.setState(context.idle_state)
        else:
            self._timer += 1


class TapEnd(State):
    def on_data(
        self, context: "StateManager", notify: Callable[[str, int], None], data: int
    ) -> None:
        notify("on_tap", 1)
        context.setState(context.idle_state)


class LongTap(State):
    def __init__(self) -> None:
        self._initial_call: bool = True

    def on_data(self, context: "StateManager", notify, data: int) -> None:
        if self._initial_call:
            notify("on_long_tap_start", 1)
            self._initial_call = False

        if data == TouchState.END_TOUCH:
            notify("on_long_tap_end", 1)
            self._initial_call = True
            context.setState(context.idle_state)
