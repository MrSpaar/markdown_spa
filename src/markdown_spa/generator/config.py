from os import environ
from os.path import exists
from dataclasses import dataclass
from importlib.util import find_spec
from configparser import ConfigParser
from typing import TypeVar, Optional, Generic


T = TypeVar("T", str, bool, int, float)


@dataclass
class Option(Generic[T]):
    """Represents an option for an extension"""

    default: T
    required: bool = True
    is_path: bool = False
    is_template: bool = False

    def __post_init__(self) -> None:
        self.is_path = self.is_path or self.is_template


@dataclass
class Dependency:
    """Represents a dependency for an extension"""

    module: str
    """The name of the module (i.e. `import <module>`)"""

    pip_package: str = ""
    """The name of the pip package (i.e. `pip install <pip_package>`, defaults to module)"""

    def __post_init__(self) -> None:
        self.pip_package = self.pip_package or self.module

    def __repr__(self) -> str:
        return self.pip_package


class IniConfig:
    """Class for loading markdown_spa config from config.ini file."""

    def __init__(self, root: str, ini_file: str = "config.ini") -> None:
        self.root = root
        self.parser = ConfigParser()
        self.parser.read(f"{root}/{ini_file}")

    def load_config(self) -> Optional[str]:
        """Load config from config.ini file (returns an optional error message)"""

        faulty_extensions = []
        self.extensions = set(self.parser.sections()) - {"DEFAULTS", "GENERATOR", "TEMPLATES"}

        for extension in self.extensions:
            if not find_spec(f"markdown_spa.extensions.{extension}"):
                faulty_extensions.append(extension)

        if faulty_extensions:
            faulty_extensions_str = "\n  - ".join(faulty_extensions)
            return f"Extensions not found: \n  - {faulty_extensions_str}"

        faulty_paths: list[str] = []
        for name, path in (
                ("pages_path", self.pages_path),
                ("assets_path", self.assets_path),
                ("templates_path", self.templates_path),
                ("base_template", f"{self.templates_path}/{self.base_template}"),
                ("nav_template", f"{self.templates_path}/{self.nav_template}")
        ):
            if not exists(path):
                faulty_paths.append(f"{name} ({path}) not found")

        if faulty_paths:
            faulty_paths_str = "\n  - ".join(faulty_paths)
            return f"Paths not found: \n  - {faulty_paths_str}"
        
        return None

    def check_options(self, section: str, options: dict[str, Option]) -> Optional[str]:
        """Check if options are valid (returns an optional error message)"""

        if not self.parser.has_section(section):
            return f"No section [{section}] found in config file"

        faulty_options: list[str] = []
        for name, option in options.items():
            if option.required and not self.parser.has_option(section, name):
                faulty_options.append(f"Required option {name} not found")
                continue

            if option.is_template:
                path = f"{self.templates_path}/{self.parser.get(section, name)}"
            else:
                path = f"{self.root}/{self.parser.get(section, name)}"

            if option.is_path and not exists(path):
                faulty_options.append(f"{name} ({path}) not found")
                continue

        if faulty_options:
            faulty_options_str = "\n  - ".join(faulty_options)
            return f"Error in section [{section}]: \n  - {faulty_options_str}"
        
        return None

    @property
    def port(self) -> int:
        """The port to run the server on"""
        if not hasattr(self, "__port"):
            self.__port = self.parser.getint(
                "GENERATOR", "port", fallback=8000
            )
        return self.__port

    @property
    def base_url(self) -> str:
        """The base url for the site"""
        if not hasattr(self, "__base_url"):
            self.__base_url = f"http://127.0.0.1:{self.port}"

            if var := environ.get("REPO"):
                user, repo = var.split("/")
                self.__base_url = f"https://{user}.github.io" if "github.io" in repo else f"https://{user}.github.io/{repo}"

        return self.__base_url

    @property
    def json(self) -> bool:
        """Whether to generate a json files for each page"""
        if not hasattr(self, "__json"):
            self.__json = self.parser.getboolean(
                "GENERATOR", "json", fallback=False
            )
        return self.__json

    @property
    def dist_path(self) -> str:
        """The path to the dist folder"""
        if not hasattr(self, "__dist_path"):
            path = self.parser.get("GENERATOR", "dist_path", fallback="generated")
            self.__dist_path = f"{self.root}/{path}"
        return self.__dist_path

    @property
    def pages_path(self) -> str:
        """The path to the pages folder"""
        if not hasattr(self, "__pages_path"):
            path = self.parser.get("GENERATOR", "pages_path", fallback="pages")
            self.__pages_path = f"{self.root}/{path}"
        return self.__pages_path

    @property
    def assets_path(self) -> str:
        """The path to the assets folder"""
        if not hasattr(self, "__assets_path"):
            path = self.parser.get("GENERATOR", "assets_path", fallback="assets")
            self.__assets_path = f"{self.root}/{path}"
        return self.__assets_path

    @property
    def dist_assets_path(self) -> str:
        """The path to the assets folder in the dist folder"""
        if not hasattr(self, "__dist_assets_path"):
            self.__dist_assets_path = f"{self.dist_path}/{self.assets_path[self.assets_path.find('/')+1:]}"
        return self.__dist_assets_path

    @property
    def templates_path(self) -> str:
        """The path to the templates folder"""
        if not hasattr(self, "__templates_path"):
            path = self.parser.get("TEMPLATES", "templates_path", fallback="templates")
            self.__templates_path = f"{self.root}/{path}"
        return self.__templates_path

    @property
    def base_template(self) -> str:
        """The path to the base template"""
        if not hasattr(self, "__base_template"):
            self.__base_template = self.parser.get(
                'TEMPLATES', 'base_template', fallback='base.html'
            )
        return self.__base_template

    @property
    def nav_template(self) -> str:
        """The path to the nav template"""
        if not hasattr(self, "__nav_template"):
            self.__nav_template = self.parser.get(
                'TEMPLATES', 'nav_template', fallback='nav.html'
            )
        return self.__nav_template

    def get(self, section: str, name: str, option: Option[T]) -> T:
        """Get option from config file"""

        if isinstance(option.default, int):
            return self.parser[section].getint(name, option.default)
        elif isinstance(option.default, float):
            return self.parser[section].getfloat(name, option.default)
        elif isinstance(option.default, bool):
            return self.parser[section].getboolean(name, option.default)
        elif isinstance(option.default, str):
            return self.parser[section].get(name, option.default)
        else:
            raise ValueError(f"Invalid type for option {name}: {type(option.default)}")

    def defaults(self) -> dict[str, str]:
        """Get default options for template variables from config file"""
        return {**self.parser["DEFAULTS"]} if self.parser.has_section("DEFAULTS") else {}
