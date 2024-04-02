from __future__ import annotations
import hid
import asyncio
from enum import IntEnum
from typing import List
# from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)
# logger.addHandler(logging.NullHandler())
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(name)s %(message)s"
                    )

VID = 0x20A0
PID = 0x42DA

# class Observer(ABC):
#     @abstractmethod
#     def update(self) -> None:
#         pass
    
# class Observable(ABC):
#     @abstractmethod
#     def on_tap(self, observer: Observer) -> None:
#         pass

#     def on_double_tap(self, observer: Observer) -> None:
#         pass

#     def on_long_tap(self, observer: Observer) -> None:
#         pass
    
#     @abstractmethod
#     def notify(self,observers: List[Observer]) -> None:
#         pass
    
    
class MuteMe():

    class LightState(IntEnum):
        OFF       = 0x00
        RED       = 0x01
        GREEN     = 0x02
        YELLOW    = 0x03
        BLUE      = 0x04
        PURPLE    = 0x05
        CYAN      = 0x06
        WHITE     = 0x07
        DIM       = 0x10
        FASTPULSE = 0x20
        SLOWPULSE = 0x30

    class DeviceState(IntEnum):
        # Data sent from MuteMe
        START_TOUCH = 0x04
        TOUCHING    = 0x01
        END_TOUCH   = 0x02
        CLEAR       = 0x00

    def __init__(self,vid,pid):
        self._vid: int = vid
        self._pid: int = pid
        self._observers: dict= {}
        self._device = hid.device()
        
        # TODO make into properties
        self._long_tap_delay = 15
        self._double_tap_delay = 13
        
        try:
            self._device.open(self._vid, self._pid)
            self._device.set_nonblocking(1)
            self.state = self.LightState.OFF
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
            logger.debug(f"Notify: event not found")
            return
        for observer in self._observers[event_type]:
            logger.debug(f"Notify: notifying - {event_type}")
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
                    logger.debug(f"Device state: {device_state}\tLong tap timer: {long_tap_timer}\tdoube tap timer: {double_tap_timer}")
                   
                    # Start touch
                    if device_state == self.DeviceState.START_TOUCH:
                        
                        if double_tap_timer:
                            if not long_tap_active and double_tap_timer < self._double_tap_delay:
                                self.notify("on_double_tap")
                                double_tap_timer = 0
                        else:
                            long_tap_timer += 1
                        
                    # Touching
                    if device_state == self.DeviceState.TOUCHING:
                        # Activate long tap if _long_tap_delay exceeded
                        if long_tap_timer >= self._long_tap_delay:
                            self.notify("on_long_tap_start")
                            long_tap_timer = 0
                            long_tap_active = True
                            
                        # increment long tap timer if enabled (not 0) 
                        if long_tap_timer:
                            long_tap_timer += 1
                   
                    # End Touch    
                    if device_state == self.DeviceState.END_TOUCH:
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
            logger.info("Canceling read event loop")
        
        except Exception as error:
            logger.critical(error)

    @property
    def state(self) -> LightState:
        return self._state

    @state.setter
    def state(self,lightState) -> None:
        self._device.write([0,lightState])
        self._state = lightState
    
    def close(self) -> None:
        self.state = self.LightState.OFF
        self._device.close()
        


# class button_event():
#     def update(button) -> None:
#         print(button.get_state())
#         if button.get_state() == MuteMe.LightState.GREEN:
#             button.set_state(MuteMe.LightState.RED)
#         else:
#             button.set_state(MuteMe.LightState.GREEN)
    
#     def on_long_press(button) -> None:
#         pass
    
#     def on_multi_tap(button) -> None:
#         pass

def on_tap(button) -> None:
    if button.state == MuteMe.LightState.GREEN:
        button.state =MuteMe.LightState.RED
    else:
        button.state = MuteMe.LightState.GREEN
        
def on_long_tap(button) -> None:
    if button.state == MuteMe.LightState.GREEN:
        button.state =MuteMe.LightState.RED
    else:
        button.state = MuteMe.LightState.GREEN

def on_double_tap(button: MuteMe) -> None:
    logger.debug(f"Before XOR: {button.state}")
    button.state = button.state ^ MuteMe.LightState.FASTPULSE
    logger.debug(f"After XOR: {button.state}")
    
myMuteMe = MuteMe(VID,PID)
myMuteMe.state = MuteMe.LightState.GREEN
myMuteMe.on_tap(on_tap)
myMuteMe.on_long_tap_start(on_long_tap)
myMuteMe.on_long_tap_end(on_long_tap)
myMuteMe.on_double_tap(on_double_tap)

async def main():
    await asyncio.gather(
        myMuteMe.connect()
        )

try:
    asyncio.run(main(), debug=False)

except KeyboardInterrupt:
    pass
        
except Exception as error:
    logger.critical(error)

finally:
    logger.warning("Shutting down...")
    myMuteMe.close()
        

