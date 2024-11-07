from abc import ABC, abstractmethod
from typing import Optional

from .devicestates import ColorState, EffectState


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
