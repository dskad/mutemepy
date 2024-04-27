from abc import ABC, abstractmethod
# from multiprocessing import context
from .enums import DeviceState
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .muteme import MuteMe


class State(ABC):
    @abstractmethod
    def on_data(self, context: 'MuteMe', data: int) -> None:
        pass

    def on_nodata(self, context: 'MuteMe') -> None:
        pass


class Idle(State):
    def on_data(self, context: 'MuteMe', data: int) -> None:
        if data == DeviceState.START_TOUCH:
            context.setState(context.start_tap_state)
    
    def on_nodata(self, context: 'MuteMe'):
        pass


class StartTap(State):
    def __init__(self):
        self._timer = 0
    
    def on_data(self, context: 'MuteMe', data: int) -> None:
        if data == DeviceState.END_TOUCH:
            self._timer = 0
            context.setState(context.multi_tap_detect_state)

        if self._timer >= context.long_tap_delay:
            self._timer = 0
            context.setState(context.long_tap_state)
        else:
            self._timer += 1
    
    def on_nodata(self, context: 'MuteMe'):
        pass


class MultiTapDetect(State):
    """
    Note:  This class should maintain an internal counter that increments on each call until
        the timer limit is exceeded. then change state to Idle
    """
    def __init__(self) -> None:
        self._timer = 0
        self._multi_touch_count = 1
        
    def on_data(self, context, data: int) -> None:
        if data == DeviceState.START_TOUCH:
            self._timer = 0
            self._multi_touch_count += 1
            context.setState(context.start_tap_state)

    def on_nodata(self, context: 'MuteMe') -> None:
        if self._timer >= context.multi_tap_delay:
            # TODO: change notify to allow notification of count of multi touch
            if self._multi_touch_count > 1:
                context.notify("on_double_tap")
            else:
                context.notify("on_tap")
                
            self._timer = 0
            self._multi_touch_count = 1
            context.setState(context.idle_state)
        else:
            self._timer += 1


class TapEnd(State):
    def on_data(self, context: 'MuteMe', data: int) -> None:
        context.notify("on_tap")
        context.setState(context.idle_state)
        
    def on_nodata(self, context: 'MuteMe'):
        pass


class LongTap(State):
    def __init__(self):
        self._initial_call: bool = True
        
    def on_data(self, context, data: int) -> None:
        if self._initial_call:
            context.notify("on_long_tap_start")
            self._initial_call = False
        
        if data == DeviceState.END_TOUCH:
            context.notify("on_long_tap_end")
            self._initial_call = True
            context.setState(context.idle_state)
        
    def on_nodata(self, context: 'MuteMe') -> None:
        pass
