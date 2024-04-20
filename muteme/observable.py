from abc import ABC, abstractmethod
from typing import List

class Observer(ABC):
    @abstractmethod
    def update(self) -> None:
        pass
    
class Observable(ABC):
    @abstractmethod
    def on_tap(self, observer: Observer) -> None:
        pass

    def on_double_tap(self, observer: Observer) -> None:
        pass

    def on_long_tap(self, observer: Observer) -> None:
        pass
    
    @abstractmethod
    def notify(self,observers: List[Observer]) -> None:
        pass