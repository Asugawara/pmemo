from abc import ABCMeta, abstractmethod

from prompt_toolkit.key_binding import KeyBindingsBase


class ExtensionBase(metaclass=ABCMeta):
    @abstractmethod
    def get_key_bindings(self) -> KeyBindingsBase:
        pass
