import asyncio
import logging
from typing import Callable, Optional
from .devicestates import ColorState
from .statemanager import StateManager
from .device import Device

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class MuteMe:
    def __init__(self) -> None:
        self._long_tap_delay = 15
        self._multi_tap_delay = 13

        self._state_manager = StateManager(self._long_tap_delay, self._multi_tap_delay)

        self._observers: dict = {}

        self._device = Device()
        self._device.open()

    @property
    def light_state(self) -> ColorState:
        return self._device.light_state

    @light_state.setter
    def light_state(self, lightState: ColorState) -> None:
        self._device.light_state = lightState

    # TODO: implement light_effect property, call to device property
    # keep track of bitmap so change in color state doesn't overwrite effect

    @property
    def long_tap_delay(self) -> int:
        return self._long_tap_delay

    @long_tap_delay.setter
    def long_tap_delay(self, delay: int) -> None:
        self._long_tap_delay = delay

    @property
    def multi_tap_delay(self) -> int:
        return self._multi_tap_delay

    @multi_tap_delay.setter
    def multi_tap_delay(self, delay: int) -> None:
        self._multi_tap_delay = delay

    # region Callbacks
    def on_tap(self, observer: Callable[[], None]) -> None:
        self._observers.setdefault("on_tap", []).append(observer)

    def on_long_tap_start(self, observer: Callable[[], None]) -> None:
        self._observers.setdefault("on_long_tap_start", []).append(observer)

    def on_long_tap_end(self, observer: Callable[[], None]) -> None:
        self._observers.setdefault("on_long_tap_end", []).append(observer)

    def on_multi_tap(self, observer: Callable[[], None]) -> None:
        self._observers.setdefault("on_double_tap", []).append(observer)

    def notify(self, event_type) -> None:
        if event_type not in self._observers:
            log.debug("Notify: event not found")
            return
        for observer in self._observers[event_type]:
            log.debug(f"Notify: notifying - {event_type}")
            observer()
    # endregion

    async def connect(self) -> None:
        try:
            while True:
                # Main event loop for button
                device_data: Optional[int] = self._device.read()

                if device_data:
                    self._state_manager.on_data(self.notify, device_data)
                else:
                    self._state_manager.on_nodata(self.notify)

                # 0.01 = 100Hz sample rate
                await asyncio.sleep(0.01)

        except asyncio.CancelledError:
            log.info("Canceling read event loop")

        except Exception as error:
            log.critical(error)
            self.close()

    def close(self) -> None:
        self.light_state = ColorState.OFF
        self._device.close()
