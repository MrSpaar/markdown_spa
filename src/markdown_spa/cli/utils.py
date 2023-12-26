from ..generator import Generator, Dependency, get_extension

from os.path import isdir
from sys import executable
from os import access, W_OK, R_OK
from importlib.util import find_spec
from typing import Callable, Optional
from subprocess import PIPE, CalledProcessError, run

from click import secho, prompt


def echo_wrap(message: str, func: Callable[..., Optional[str]], *args, **kwargs) -> Optional[str]:
    secho(f"{message}... ", nl=False)
    err = func(*args, **kwargs)

    if err:
        secho("failed", fg="red", bold=True)
        return err
    
    secho(f"done", fg="green", bold=True)


def silent_call(command) -> Optional[str]:
    try:
        run(
            command,
            shell=True, check=True,
            stdout=PIPE, stderr=PIPE
        )
    except CalledProcessError as e:
        return e.stderr.decode('utf-8')


def check_dir(path: str) -> Optional[str]:
    if not isdir(path):
        return f"Directory '{path}' not found!"

    if not access(path, W_OK) or not access(path, R_OK):
        return f"Directory '{path}' not accessible!"


def ensure_installed(dependency: Dependency) -> Optional[str]:
    if not find_spec(dependency.module):
        return silent_call(f"{executable} -m pip install {dependency.pip_package}")


def initialize_extension(extension: str) -> Optional[str]:
    module = get_extension(extension)
    if not module:
        return f"Extension {extension} not found!"

    values = {
        name: prompt(
            f"Enter {name} (default: {option.default})", default=option.default,
            prompt_suffix=": ", show_default=False, type=type(option.default)
        ) for name, option in module.OPTIONS.items()
    }

    for pip_package in module.DEPENDENCIES:
        if err := ensure_installed(pip_package):
            return err

    module.initialize(**values)    
    with open("config.ini", "a") as file:
        file.write(f"\n[{extension}]\n")
        for key, value in values.items():
            file.write(f"{key} = {value}\n")


def build_project(generator: Generator) -> int:
    if err := echo_wrap("Loading config", generator.load_config):
        secho(err)
        return 1

    for extension in generator.extensions:
        for dependency in extension.DEPENDENCIES:
            if err := echo_wrap(f"Searching for {dependency}", ensure_installed, dependency):
                secho(err)
                return 1

    if err := echo_wrap("Copying assets", generator.copy_assets):
        secho(err)
        return 1

    if err := echo_wrap("Rendering pages", generator.render_pages):
        secho(err)
        return 1

    for extension in generator.extensions:
        if err := echo_wrap(f"Rendering '{extension.__class__.__name__}' extension", extension.render):
            secho(err)
            return 1

    secho("Project built!", fg="green", bold=True)
    return 0
