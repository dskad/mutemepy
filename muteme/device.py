from time import sleep
from typing import Optional
import hid
import logging
from .enums import DeviceState, LightState
from .exceptions import DeviceNotFoundError

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

class Device():
    def __init__(self):
        self._supported_devices = [
            (0x16c0, 0x27db),
            (0x20a0, 0x42da),
            (0x20a0, 0x42db) 
        ]

        self._device = hid.device()
        self._light_state = LightState.OFF

    @property
    def light_state(self) -> LightState:
        return self._light_state

    @light_state.setter
    def light_state(self, lightState: LightState) -> None:
        # log.debug(f"Setting light state to {LightState(lightState).name}")
        self._device.write([0, lightState])
        self._light_state = lightState
    
    def open(self):
        log.debug("Opening device")
        for vid,pid in self._supported_devices:
            try:
                log.debug(f"Attempting to open: ({hex(vid)},{hex(pid)})")
                self._device.open(vid, pid)
                self._device.set_nonblocking(1)
                break
            except IOError:
                log.debug(f"IOError for ({hex(vid)},{hex(pid)}), Device not found")
                
        try:
            log.debug(f"Clearing device ({hex(vid)},{hex(pid)}) read buffer")
            
            # counting nulls because the device appears to always send a null on first read
            # and sometimes mixed in with the buffer data. (I might be reading too fast)
            null_count = 0
            while null_count < 5:
                data = self._device.read(8)
                log.debug(f"Clearing buffer: {data}")
                if data == [0x0]*8:
                    break
                elif data == []:
                    null_count += 1
                sleep(.01)
            
        except ValueError as error:
            log.error(f"Compatible MuteMe device not found: {error}")
            raise DeviceNotFoundError("Device not found")
        
        self.light_state = LightState.OFF

    def read(self) -> Optional[int]:
        data = self._device.read(8)
        if data:
            log.debug(f"Read data: {DeviceState(data[3]).name}")
            return data[3]
        else:
            return data
    
    def close(self) -> None:
        self._device.close()