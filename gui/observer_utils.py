from typing import List, Callable

# Define the Observer interface
class Observer:
    def call(self, event: str, *args, **kwargs):
        raise NotImplementedError

# Define the Observable (Subject) interface
class Observable:
    def __init__(self):
        self._observers: List[Observer] = []

    def add_observer(self, observer: Observer):
        self._observers.append(observer)

    def remove_observer(self, observer: Observer):
        self._observers.remove(observer)

    def notify_observers(self, event: str, *args, **kwargs):
        for observer in self._observers:
            observer.call(event, *args, **kwargs)
