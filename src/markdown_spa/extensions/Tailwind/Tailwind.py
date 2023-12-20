from .. import Extension
from ...packages import enable

from os import remove
from shutil import copy
from click import prompt
from os.path import exists
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...generator import Generator


class Tailwind(Extension):
    def __init__(self, generator: 'Generator') -> None:
        super().__init__(generator)
        self.config.check_options(self.name, ("config_file", True))
        
        self.input_file = f"{self.config.root}/{self.config.get(self.name, 'input_file')}"
        self.config_file = f"{self.config.root}/{self.config.get(self.name, 'config_file')}"

        self.to_watch = [self.input_file, self.config_file, self.config.pages_path, self.config.templates_path]

    @staticmethod
    def initialize() -> None:
        if enable("pytailwindcss", "pytailwindcss") != 0:
            return

        input_file = prompt(
            "Enter the input file (default: assets/style.css)",
            default="", prompt_suffix=": ", show_default=False
        )

        config_file = prompt(
            "Enter the config file (default: tailwind.config.js)",
            default="tailwind.config.js", prompt_suffix=": ", show_default=False
        )

        copy(f"{Tailwind.path}/tailwind.config.js", config_file)

        with open(f"config.ini", "a") as file:
            file.write(f"\n[Tailwind]\ninput_file = {input_file}\nconfig_file = {config_file}\n")

        if exists("./assets/style.css"):
            remove("./assets/style.css")

        if not input_file:
            with open(input_file, "w") as file:
                file.write("@tailwind base;\n@tailwind components;\n@tailwind utilities;\n\n")

    def render(self) -> None:
        from pytailwindcss import run

        cli_args = f"-c {self.config_file} -o {self.config.dist_assets_path}/style.css"
        if self.config.has_option(self.name, "input_file"):
            cli_args += f" -i {self.input_file}"

        run(auto_install=True, tailwindcss_cli_args=cli_args)
