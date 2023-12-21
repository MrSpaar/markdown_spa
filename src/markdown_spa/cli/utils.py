from ..generator import Generator, Dependency, get_extension

from importlib.util import find_spec
from typing import Callable, Optional
from subprocess import PIPE, CalledProcessError, run

from click import echo as _echo, style, prompt


def echo(message: str, nl=True, **kwargs) -> None:
    _echo(style(message, **kwargs), nl=nl)


def echo_wrap(message: str, func: Callable[..., Optional[str]], *args, **kwargs) -> Optional[str]:
    echo(f"{message}... ", nl=False)
    err = func(*args, **kwargs)
    echo(f"done", fg="green", bold=True)
    return err


def silent_call(command) -> Optional[str]:
    try:
        run(
            command,
            shell=True, check=True,
            stdout=PIPE, stderr=PIPE
        )
    except CalledProcessError as e:
        return e.stderr.decode('utf-8')


def ensure_installed(dependency: Dependency) -> Optional[str]:
    if not find_spec(dependency.module):
        return silent_call(f"pip install {dependency.pip_package}")


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
            echo("failed.", fg="red", bold=True)
            echo(err)
            return
        
    echo("done", fg="green", bold=True)
    module.initialize(**values)
    
    with open("config.ini", "a") as file:
        file.write(f"\n[{extension}]\n")
        for key, value in values.items():
            file.write(f"{key} = {value}\n")


def build_project(generator: Generator) -> int:
    if err := echo_wrap("Loading config", generator.load_config):
        echo(err)
        return 1

    for extension in generator.extensions:
        for dependency in extension.DEPENDENCIES:
            if err := echo_wrap(f"Searching for {dependency}", ensure_installed, dependency):
                echo(err)
                return 1

    if err := echo_wrap("Copying assets", generator.copy_assets):
        echo(err)
        return 1

    if err := echo_wrap("Rendering pages", generator.render_pages):
        echo(err)
        return 1

    for extension in generator.extensions:
        if err := echo_wrap(f"Rendering '{extension.__class__.__name__}' extension", extension.render):
            echo(err)
            return 1

    echo("Project built!", fg="green", bold=True)
    return 0
