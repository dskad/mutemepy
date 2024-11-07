import asyncio
import logging
from typing import Callable, Optional

from .abstractclasses import AbstractDevice
from .device import Device
from .devicestates import ColorState, EffectState
from .statemanager import StateManager

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class MuteMe:
    def __init__(
        self,
        long_tap_delay: int = 15,
        multi_tap_delay: int = 13,
        device: AbstractDevice = Device(),
    ) -> None:
        self._long_tap_delay = long_tap_delay
        self._multi_tap_delay = multi_tap_delay

        self._state_manager: StateManager = StateManager(
            self._long_tap_delay, self._multi_tap_delay
        )

        self._observers: dict = {}

        self._device: AbstractDevice = device
        self._device.open()

    @property
    def color(self) -> ColorState:
        return self._device.color

    @color.setter
    def color(self, new_color: ColorState) -> None:
        self._device.color = new_color

    @property
    def effect(self) -> EffectState:
        return self._device.effect

    @effect.setter
    def effect(self, new_effect: EffectState) -> None:
        self._device.effect = new_effect

    @property
    def long_tap_delay(self) -> int:
        return self._long_tap_delay

    @property
    def multi_tap_delay(self) -> int:
        return self._multi_tap_delay

    def on_tap(self, observer: Callable[[int], None]) -> None:
        self._observers.setdefault("on_tap", []).append(observer)

    def on_long_tap_start(self, observer: Callable[[int], None]) -> None:
        self._observers.setdefault("on_long_tap_start", []).append(observer)

    def on_long_tap_end(self, observer: Callable[[int], None]) -> None:
        self._observers.setdefault("on_long_tap_end", []).append(observer)

    def on_multi_tap(self, observer: Callable[[int], None]) -> None:
        self._observers.setdefault("on_multi_tap", []).append(observer)

    def notify(self, event_type, event_count) -> None:
        if event_type not in self._observers:
            log.error("Notify: event not found")
            return
        for observer in self._observers[event_type]:
            log.debug(f"Notify: notifying - {event_type}")
            observer(event_count)

    async def _event_loop(self) -> None:
        try:
            while True:
                # Main event loop for button
                device_data: Optional[int] = self._device.read_touch()

                if device_data:
                    self._state_manager.on_data(self.notify, device_data)
                else:
                    self._state_manager.on_tick(self.notify)

                # 0.01 = 100Hz sample rate
                await asyncio.sleep(0.01)

        except asyncio.CancelledError:
            log.info("Canceling read event loop")

        except Exception as error:
            log.critical(error)
            self.close()

    def connect(self) -> None:
        asyncio.run(self._event_loop())

    def close(self) -> None:
        self.color = ColorState.OFF
        self._device.close()
