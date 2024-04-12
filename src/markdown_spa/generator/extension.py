from pathlib import Path
from importlib import import_module
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Type, final

from .config import Option, Dependency, T

if TYPE_CHECKING:
    from . import Generator


class Extension(ABC):
    """Base abstract class for all extensions"""

    OPTIONS: dict[str, Option] = {}
    """A dict of options for the extension"""

    DEPENDENCIES: tuple[Dependency, ...] = ()
    """A list of dependencies for the extension (will be installed if not already)"""

    def __init__(self, generator: 'Generator') -> None:
        self.generator = generator
        self.config = generator.config

    @property
    @abstractmethod
    def TO_WATCH(cls) -> list[str]:
        """A list of paths to watch for changes"""
        ...

    @abstractmethod
    def render(self) -> None:
        """Called either via `markdown_spa build` or `markdown_spa watch` (if TO_WATCH is not empty)"""
        ...

    @staticmethod
    @abstractmethod
    def initialize(**kwargs) -> None:
        """Called when the extension is added to a project, either via `markdown_spa init` or `markdown_spa add`"""
        ...

    @final
    @classmethod
    def PATH(cls) -> str:
        """The path to the extension (cannot be overridden)"""
        return f"{(Path(__file__).parent.parent / 'extensions').absolute()}/{cls.__name__}"

    @final
    def get_option(self, name: str) -> T:
        """Gets an option from the extension's config."""
        return self.config.get(self.__class__.__name__, name, self.OPTIONS[name])


def get_extension(name: str) -> Type[Extension]:
    return getattr(import_module(f"markdown_spa.extensions.{name}"), name)
