from ...config import ensure_lib
from ..extension import Extension

from shutil import copy
from os.path import exists
from os import makedirs, remove
from importlib import import_module
from typing import TYPE_CHECKING

from click import prompt

if TYPE_CHECKING:
    from ...generator import Generator 


class SASS(Extension):
    def __init__(self, generator: 'Generator') -> None:
        super().__init__(generator)

        self.check_options(("main_path", True), ("source_path", True))
        self.to_watch = [
            f"{self.config.root}/{self.config.get(self.name, 'source_path')}"
        ]

        self.main_path = f"{self.config.root}/{self.config.get(self.name, 'main_path')}"

    @staticmethod
    def initialize() -> None:
        if not ensure_lib("sass", "libsass"):
            raise Exception("Failed to install lib 'libsass'")

        source_path = prompt(
            "Enter the folder containing all SASS files (default: ./sass)",
            default="sass", prompt_suffix=": ", show_default=False
        )
        
        main_path = prompt(
            "Enter the main SASS file (default: main.scss)",
            default=f"main.scss", prompt_suffix=": ", show_default=False
        )

        if exists("./assets/style.css"):
            remove("./assets/style.css")

        makedirs(source_path, exist_ok=True)
        copy(f"{SASS.path}/main.scss", f"{source_path}/{main_path}")

        with open("config.ini", "a") as file:
            file.write(f"\n[SASS]\nsource_path = {source_path}\nmain_path = {source_path}/{main_path}\n")

    def render(self) -> None:
        if not ensure_lib("sass", "libsass"):
            return
        
        with open(f"{self.config.dist_assets_path}/style.css", "w") as f:
            from sass import compile
            f.write(compile(filename=self.main_path, output_style="compressed"))
