from collections import defaultdict
from typing import Callable, Optional


class NumberState():
    def __init__(self):
        self._number = 0

        self.callbacks: Dict[str, List[Callable]] = defaultdict(list)

    # event handler registration

    def on(self, event: str, func: Optional[Callable] = None):
        def subscribe(func: Callable):
            if not callable(func):
                raise ValueError("Argument func must be callable.")
            self.callbacks[event].append(func)
            return func
        if func is None:
            return subscribe
        subscribe(func)

    # generate (emit) events
    def emit(self, event, message):
        for callback in self.callbacks[event]:
            callback(message)

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, new_value):
        if new_value != self._number:
            if new_value >= 0xff:
                new_value = 0
            self._number = new_value
