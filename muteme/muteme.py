import hid
import asyncio
import logging
from .enums import DeviceState, LightState

# from typing import List
# from abc import ABC, abstractmethod

log = logging.getLogger(__name__)
# logger.addHandler(logging.NullHandler())

class MuteMe():
    def __init__(self,vid,pid):
        self._vid: int = vid
        self._pid: int = pid
        self._observers: dict= {}
        self._device = hid.device()
        
        # TODO: make into properties
        self._long_tap_delay = 15
        self._double_tap_delay = 13
        
        try:
            self._device.open(self._vid, self._pid)
            self._device.set_nonblocking(1)
            self.lightState = LightState.OFF
        except:
            print("Error connecting to device")

    def on_tap(self, observer: callable) -> None:
        self._observers.setdefault("on_tap",[]).append(observer)
        
    def on_long_tap_start(self, observer: callable) -> None:
        self._observers.setdefault("on_long_tap_start",[]).append(observer)
        
    def on_long_tap_end(self, observer: callable) -> None:
        self._observers.setdefault("on_long_tap_end",[]).append(observer)
        
    def on_double_tap(self, observer: callable) -> None:
        self._observers.setdefault("on_double_tap",[]).append(observer)
        
        
    def notify(self,event_type) -> None:
        if not event_type in self._observers:
            log.debug(f"Notify: event not found")
            return
        for observer in self._observers[event_type]:
            log.debug(f"Notify: notifying - {event_type}")
            observer(self)

    async def connect(self) -> None:

        try: 
            double_tap_timer = 0
            long_tap_timer = 0
            long_tap_active = False
            
            while True:
                if double_tap_timer:
                    if double_tap_timer <= self._double_tap_delay:
                        double_tap_timer += 1
                    else:
                        self.notify("on_tap")
                        double_tap_timer = 0
                        
                device_data = self._device.read(8)

                if device_data:
                    device_state = device_data[3]
                    log.debug(f"Device state: {device_state}\tLong tap timer: {long_tap_timer}\tdoube tap timer: {double_tap_timer}")
                   
                    # Start touch
                    if device_state == DeviceState.START_TOUCH:
                        
                        if double_tap_timer:
                            if not long_tap_active and double_tap_timer < self._double_tap_delay:
                                self.notify("on_double_tap")
                                double_tap_timer = 0
                        else:
                            long_tap_timer += 1
                        
                    # Touching
                    if device_state == DeviceState.TOUCHING:
                        # Activate long tap if _long_tap_delay exceeded
                        if long_tap_timer >= self._long_tap_delay:
                            self.notify("on_long_tap_start")
                            long_tap_timer = 0
                            long_tap_active = True
                            
                        # increment long tap timer if enabled (not 0) 
                        if long_tap_timer:
                            long_tap_timer += 1
                   
                    # End Touch    
                    if device_state == DeviceState.END_TOUCH:
                        if long_tap_active:
                            self.notify("on_long_tap_end")
                            long_tap_active = False
                            long_tap_timer = 0
                        elif double_tap_timer:
                            double_tap_timer = 0
                            long_tap_timer = 0
                        else:
                            double_tap_timer +=1
                            long_tap_timer = 0

                # 0.01 = 100Hz sample rate
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            log.info("Canceling read event loop")
        
        except Exception as error:
            log.critical(error)

    @property
    def lightState(self) -> LightState:
        return self._state

    @lightState.setter
    def lightState(self,lightState) -> None:
        self._device.write([0,lightState])
        self._state = lightState
    
    def close(self) -> None:
        self.lightState = LightState.OFF
        self._device.close()
        