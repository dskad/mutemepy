import hid
import asyncio
import logging
from typing import List, Callable
from .enums import LightState
from .statemanager import StateManager

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class MuteMe:

    def __init__(self, vid, pid):
        self._vid: int = vid
        self._pid: int = pid
        self._device = hid.device()
        self._long_tap_delay = 15
        self._multi_tap_delay = 13

        self._state_manager = StateManager(self._long_tap_delay, self._multi_tap_delay)

        self._observers: dict = {}

        try:
            self._device.open(self._vid, self._pid)
            self._device.set_nonblocking(1)
            self.light_state = LightState.OFF
        except Exception:
            #TODO: fix exception type
            print("Error connecting to device")

    
    @property
    def light_state(self) -> LightState:
        return self._light_state

    @light_state.setter
    def light_state(self, lightState: LightState) -> None:
        self._device.write([0, lightState])
        self._light_state = lightState

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
    def on_tap(self, observer: callable) -> None:
        self._observers.setdefault("on_tap", []).append(observer)

    def on_long_tap_start(self, observer: callable) -> None:
        self._observers.setdefault("on_long_tap_start", []).append(observer)

    def on_long_tap_end(self, observer: callable) -> None:
        self._observers.setdefault("on_long_tap_end", []).append(observer)

    def on_double_tap(self, observer: callable) -> None:
        self._observers.setdefault("on_double_tap", []).append(observer)

    def notify(self, event_type) -> None:
        if  event_type not in self._observers:
            log.debug("Notify: event not found")
            return
        for observer in self._observers[event_type]:
            log.debug(f"Notify: notifying - {event_type}")
            observer(self)
    # endregion

    
    async def connect(self) -> None:
        try:
            while True:
                # Main event loop for button 
                device_data: List[int] = self._device.read(8)
               
                if device_data:
                    self._state_manager.on_data(self.notify, device_data[3])
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
        self.light_state = LightState.OFF
        self._device.close()
