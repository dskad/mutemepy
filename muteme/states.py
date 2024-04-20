from abc import ABC, abstractmethod

class State(ABC):
    @property
    def context(self) -> MuteMe:
        return self._context
    
    @context.setter
    def context(self, context: MuteMe) -> None:
        self._context = context
    
    @abstractmethod
    def set_state():
        pass

    @abstractmethod
    def on_data():
        pass

class Idle(State):
    def set_state():
        pass
    
    def on_data():
        pass
    