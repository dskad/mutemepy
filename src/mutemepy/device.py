import logging
from abc import ABC, abstractmethod
from time import sleep
from typing import Optional

import hid

from .devicestates import ColorState, EffectState, TouchState
from .exceptions import DeviceNotFoundError

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class AbstractDevice(ABC):
    @property
    @abstractmethod
    def color(self) -> ColorState:
        pass

    @color.setter
    @abstractmethod
    def color(self, new_color: ColorState) -> None:
        pass

    @property
    @abstractmethod
    def effect(self) -> EffectState:
        pass

    @effect.setter
    @abstractmethod
    def effect(self, new_effect: EffectState) -> None:
        pass

    @abstractmethod
    def open(self) -> None:
        pass

    @abstractmethod
    def read_touch(self) -> Optional[int]:
        pass

    @abstractmethod
    def close(self) -> None:
        pass


class Device(AbstractDevice):
    def __init__(self) -> None:
        self._supported_devices = [
            (0x16C0, 0x27DB),  # MuteMe Original (prototypes)
            (0x20A0, 0x42DA),  # MuteMe Original (production)
            (0x20A0, 0x42DB),  # MuteMe Mini (production)
        ]

        self._device = hid.device()
        self._display_state = 0x00

    @property
    def color(self) -> ColorState:
        color = self._display_state & 0x0F
        return ColorState(color)

    @color.setter
    def color(self, new_color: ColorState) -> None:
        log.debug(f"Setting light state to {ColorState(new_color).name}")
        current_effect = self._display_state & 0xF0
        self._display_state = new_color | current_effect
        try:
            self._device.write([0, self._display_state])
        except IOError as e:
            log.critical(f"Device not open or found: {e}")
            raise IOError("Device not found or open while writing")

    @property
    def effect(self) -> EffectState:
        effect = self._display_state & 0xF0
        return EffectState(effect)

    @effect.setter
    def effect(self, new_effect: EffectState) -> None:
        log.debug(f"Setting light effect to {EffectState(new_effect).name}")
        current_color = self._display_state & 0x0F
        self._display_state = new_effect | current_color
        try:
            self._device.write([0, self._display_state])
        except IOError as e:
            log.critical(f"Device not open or found: {e}")
            raise IOError("Device not found or open while writing")

    def open(self) -> None:
        log.debug("Opening device")
        for vid, pid in self._supported_devices:
            try:
                log.debug(f"Attempting to open: ({hex(vid)},{hex(pid)})")
                self._device.open(vid, pid)
                self._device.set_nonblocking(1)
                break
            except IOError:
                # NOTE: The exception of no device connected after trying all device IDs is
                # caught in the try block below. Connection errors are purposely ignored here
                log.debug(f"IOError for ({hex(vid)},{hex(pid)}), Device not found")

        try:
            manufacturer = self._device.get_manufacturer_string()
            product = self._device.get_product_string()
            serial_number = self._device.get_serial_number_string()
            log.info(
                f"Found Device: manufacturer: {manufacturer}, product: {product}, serial number: {serial_number}"
            )

        except ValueError as error:
            log.error(f"Compatible MuteMe device not found: {error}")
            raise DeviceNotFoundError("Device not found")

        # counting nulls because the device appears to always send a null on first read
        # and sometimes mixed in with the buffer data. (I might be reading too fast)
        # 4 consecutive nulls appears to indicate there is no more data to read
        null_count = 0
        while null_count < 5:
            data = self._device.read(8)
            log.debug(f"Deleting buffer data: {data}")
            if data == [0x0] * 8:
                break
            elif data == []:
                null_count += 1
            sleep(0.01)

        self.effect = EffectState.OFF
        self.color = ColorState.OFF

    def read_touch(self) -> Optional[int]:
        data = self._device.read(8)
        if data:
            log.debug(f"Read data: {TouchState(data[3]).name}")
            return data[3]
        else:
            # No data in the buffer, so null is returned from read
            return data

    def close(self) -> None:
        self._device.close()
