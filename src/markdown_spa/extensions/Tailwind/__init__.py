from os import remove
from shutil import copy
from os.path import exists

from ...generator import Extension, Dependency, Option


class Tailwind(Extension):
    DEPENDENCIES = (
        Dependency("pytailwindcss"),
    )
    OPTIONS = {
        "config_file": Option(default="tailwind.config.js", is_path=True),
        "input_file": Option(default="assets/style.css", is_path=True, required=False),
    }

    def render(self) -> None:
        cli_args = f"-c {self.get_option('config_file')} -o {self.config.dist_assets_path}/style.css"

        if input_file := self.get_option("input_file"):
            cli_args += f" -i {self.config.root+'/'}{input_file}"

        from pytailwindcss import run
        run(auto_install=True, tailwindcss_cli_args=cli_args)

    @staticmethod
    def initialize(**kwargs) -> None:
        copy(f"{Tailwind.PATH}/tailwind.config.js", kwargs["config_file"])

        if exists("./assets/style.css"):
            remove("./assets/style.css")

        if kwargs["input_file"]:
            with open(kwargs["input_file"], "w", encoding="utf-8") as file:
                file.write("@tailwind base;\n@tailwind components;\n@tailwind utilities;\n\n")
