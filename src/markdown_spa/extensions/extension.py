from pathlib import Path
from importlib import import_module
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Type, Optional

if TYPE_CHECKING:
    from ..generator import Generator


class Extension(ABC):
    def __init__(self, generator: 'Generator') -> None:
        self.name = self.__class__.__name__
        self.to_watch: list[str] = []

        self.generator = generator
        self.config = generator.config

        if not generator.config.has_section(self.name):
            raise Exception(f"Missing [{self.name}] section in config.ini")

    def check_options(self, *options: tuple[str, bool]) -> None:
        self.generator.config.check_options(self.name, *options)

    @staticmethod
    @abstractmethod
    def initialize() -> None:
        ...

    @abstractmethod
    def render(self) -> None:
        ...

    @classmethod
    @property
    def path(cls) -> str:
        return f"{Path(__file__).parent.absolute()}/{cls.__name__}"
    
    @staticmethod
    def get_module(name: str) -> Optional[Type["Extension"]]:
        try:
            return getattr(import_module(f"markdown_spa.extensions.{name}"), name)
        except (ImportError, AttributeError):
            return None
