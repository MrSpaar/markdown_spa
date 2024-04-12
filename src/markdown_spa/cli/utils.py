from os.path import isdir
from sys import executable
from os import access, W_OK, R_OK
from importlib.util import find_spec
from typing import Callable, Optional
from subprocess import PIPE, CalledProcessError, run

from click import secho, prompt
from ..generator import Generator, Dependency, get_extension


def echo_wrap(message: str, func: Callable[..., Optional[str]], *args, full_tb: bool = False, **kwargs) -> Optional[str]:
    secho(f"{message}... ", nl=False)

    try:
        err = func(*args, **kwargs)
    except Exception as e:
        if full_tb:
            secho("failed", fg="red", bold=True)
            raise e
        err = str(e)

    if err:
        secho("failed", fg="red", bold=True)
        return err

    secho("done", fg="green", bold=True)
    return None


def call(command) -> Optional[str]:
    try:
        run(
            command,
            shell=True, check=True,
            stdout=PIPE, stderr=PIPE
        )
    except CalledProcessError as e:
        try:
            return e.stderr.decode('utf-8')
        except UnicodeDecodeError:
            return "Could not error output to utf-8"
    
    return None


def check_dir(path: str) -> Optional[str]:
    if not isdir(path):
        return f"Directory '{path}' not found!"

    if not access(path, W_OK) or not access(path, R_OK):
        return f"Directory '{path}' not accessible!"
    
    return None


def ensure_installed(dependency: Dependency) -> Optional[str]:
    if not find_spec(dependency.module):
        return call(f"{executable} -m pip install {dependency.pip_package}")
    
    return None


def initialize_extension(extension: str, full_tb: bool = False) -> Optional[str]:
    try:
        module = get_extension(extension)
    except Exception as e:
        if full_tb:
            raise e
        return f"Extension {extension} not found!"
    
    return None

    values = {
        name: prompt(
            f"Enter {name} (default: {option.default})", default=option.default,
            prompt_suffix=": ", show_default=False, type=type(option.default)
        ) for name, option in module.OPTIONS.items()
    }

    for pip_package in module.DEPENDENCIES:
        if err := ensure_installed(pip_package):
            return err

    try:
        module.initialize(**values)
    except Exception as e:
        if full_tb:
            raise e
        return f"Failed to initialize {extension}: {e}"

    with open("config.ini", "a") as file:
        file.write(f"\n[{extension}]\n")
        for key, value in values.items():
            file.write(f"{key} = {value}\n")


def build_project(generator: Generator) -> int:
    if err := echo_wrap("Loading config", generator.load_config, full_tb=generator.full_tb):
        secho(err)
        return 1

    for extension in generator.extensions:
        for dependency in extension.DEPENDENCIES:
            if err := echo_wrap(f"Searching for {dependency}", ensure_installed, dependency):
                secho(err)
                return 1

    if err := echo_wrap("Copying assets", generator.copy_assets, full_tb=generator.full_tb):
        secho(err)
        return 1

    if err := echo_wrap("Rendering pages", generator.render_pages, full_tb=generator.full_tb):
        secho(err)
        return 1

    for extension in generator.extensions:
        if err := echo_wrap(f"Rendering '{extension.__class__.__name__}' extension", extension.render, full_tb=generator.full_tb):
            secho(err)
            return 1

    secho("Project built!", fg="green", bold=True)
    return 0
