import hid
import asyncio
import logging
from typing import List
from .enums import LightState
from .states import State, Idle, StartTap, TapEnd,  MultiTapDetect, LongTap

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class MuteMe:

    def __init__(self, vid, pid):
        self._vid: int = vid
        self._pid: int = pid
        self._device = hid.device()
        self._long_tap_delay = 15
        self._multi_tap_delay = 13

        self._observers: dict = {}

        self._idle_state = Idle()
        self._start_tap_state = StartTap()
        self._tap_end_state = TapEnd()
        self._multi_tap_detect_state = MultiTapDetect()
        self._long_tap_state = LongTap()

        self.setState(self._idle_state)

        try:
            self._device.open(self._vid, self._pid)
            self._device.set_nonblocking(1)
            self.light_state = LightState.OFF
        except Exception:
            #TODO: fix exception type
            print("Error connecting to device")

    
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


    def setState(self, state: State):
        self._button_state = state

    def on_data(self, data: int):
        self._button_state.on_data(self, data)
        
    def on_nodata(self):
        self._button_state.on_nodata(self)

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
            # double_tap_timer = 0
            # long_tap_timer = 0
            # long_tap_active = False

            while True:
                # Note: Don't count the double tap timer here. on every cycle through this loop, call on_data
                #   so that multitap detect can increment it's timer counter.

                # if double_tap_timer:
                #     if double_tap_timer <= self._double_tap_delay:
                #         double_tap_timer += 1
                #     else:
                #         self.notify("on_tap")
                #         double_tap_timer = 0

                device_data: List[int] = self._device.read(8)

                # NOTE: device_data is null when there is no device input. there's no index 3 on null...
                #       Need to figure out how to call on_data with null device_data or device_data[3]
                
                if device_data:
                    self.on_data(device_data[3])
                else:
                    self.on_nodata()

                # Note: Move detection of data present into the state on_data functions. This allows for timers to increment
                #   Null data will either do nothing in the Idle state or increment a timer in the multitap detect state.

                # if device_data:
                #     device_state: int = device_data[3]
                #     log.debug(
                #         f"Device state: {device_state}\tLong tap timer: {long_tap_timer}\tdoube tap timer: {double_tap_timer}"
                #     )

                #     # Start touch
                #     if device_state == DeviceState.START_TOUCH:
                #         if double_tap_timer:
                #             if (
                #                 not long_tap_active
                #                 and double_tap_timer < self._double_tap_delay
                #             ):
                #                 self.notify("on_double_tap")
                #                 double_tap_timer = 0
                #         else:
                #             long_tap_timer += 1

                #     # Touching
                #     if device_state == DeviceState.TOUCHING:
                #         # Activate long tap if _long_tap_delay exceeded
                #         if long_tap_timer >= self._long_tap_delay:
                #             self.notify("on_long_tap_start")
                #             long_tap_timer = 0
                #             long_tap_active = True

                #         # increment long tap timer if enabled (not 0)
                #         if long_tap_timer:
                #             long_tap_timer += 1

                #     # End Touch
                #     if device_state == DeviceState.END_TOUCH:
                #         if long_tap_active:
                #             self.notify("on_long_tap_end")
                #             long_tap_active = False
                #             long_tap_timer = 0
                #         elif double_tap_timer:
                #             double_tap_timer = 0
                #             long_tap_timer = 0
                #         else:
                #             double_tap_timer += 1
                #             long_tap_timer = 0

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
