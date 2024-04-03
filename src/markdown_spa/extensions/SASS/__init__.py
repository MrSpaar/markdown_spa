from shutil import copy
from os.path import exists
from os import makedirs, remove

from ...generator import Extension, Dependency, Option


class SASS(Extension):
    DEPENDENCIES = (
        Dependency("sass", "libsass"),
    )
    OPTIONS = {
        "source_path": Option(default="scss", is_path=True),
        "main_path": Option(default="scss/main.scss", is_path=True)
    }

    @property
    def TO_WATCH(self) -> list:
        return [
            f"{self.config.root}/{self.get_option('source_path')}"
        ]

    def render(self) -> None:
        from sass import compile

        with open(f"{self.config.dist_assets_path}/style.css", "w") as f:
            f.write(compile(
                output_style="compressed",
                filename=f"{self.config.root}/{self.get_option('main_path')}"
            ))

    @staticmethod
    def initialize(**kwargs) -> None:
        if exists("./assets/style.css"):
            remove("./assets/style.css")

        makedirs(kwargs["source_path"], exist_ok=True)
        copy(f"{SASS.PATH}/main.scss", kwargs['main_path'])
