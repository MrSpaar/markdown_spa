from .generator import Generator
from ..extensions import Extension
from ..packages import enable, silent_call

from requests import get
from os.path import exists
from os import listdir, chdir
from shutil import copytree, rmtree
from typing import Callable, TypeVar
from importlib_metadata import version

from click import Path, Choice, group, option, argument, prompt, echo as _echo, style


def echo(message: str, nl=True, **kwargs) -> None:
    _echo(style(message, **kwargs), nl=nl)

T = TypeVar("T")
def echo_wrap(message: str, func: Callable[..., T], *args, **kwargs) -> T:
    echo(f"{message}... ", nl=False)

    try:
        res = func(*args, **kwargs)
        echo(f"done", fg="green", bold=True)
        return res
    except Exception as e:
        echo(f"failed\nError: ", fg="red", bold=True, nl=False)
        echo(str(e))
        exit(1)


@group()
def main() -> int:
    """Static site generator for Markdown files."""
    
    current = version("markdown-spa")
    latest = get("https://pypi.org/pypi/markdown-spa/json").json()["info"]["version"]

    if latest > current:
        echo(f"Version {latest} is available, run 'pip install -U markdown-spa' to update.", fg="yellow", bold=True)

    return 0


@main.command()
@argument("path", default=".")
def init(path: str) -> int:
    """Create a blank Markdown-SPA project"""

    if exists(path):
        echo("A file or directory with that name already exists!", fg="red", bold=True)
        return 1

    echo("Cloning blank project... ", nl=False)
    if silent_call(f"git clone --depth=1 https://github.com/MrSpaar/Markdown-SPA.git --no-checkout {path}") != 0:
        echo("failed.", fg="red", bold=True)
        return 1

    chdir(path)
    commands = (
        "git config core.sparseCheckout true",
        "echo 'blank/' >> .git/info/sparse-checkout",
        "git checkout"
    )

    for command in commands:
        if silent_call(command) != 0:
            echo("failed.", fg="red", bold=True)
            return 1

    copytree("blank", ".", dirs_exist_ok=True); rmtree("blank")
    echo("done.", fg="green", bold=True)

    dirs = [
        path for path in listdir(f"{__file__[:-7]}/../extensions")
        if not path.endswith(".py") and not path.startswith("__")
    ]
    
    dirs_str = "\n  - ".join(["", *dirs])
    inp = prompt(
        f"Choose extensions to enable: {dirs_str}\n",
        type=str, prompt_suffix="> ", default="", show_default=False
    )

    if not inp:
        echo("Project initialized!", fg="green", bold=True)
        return 0

    extensions = inp.split(" ")
    if diff := set(extensions).difference(dirs):
        echo(f"Unknown extensions: {', '.join(diff)}", fg="red", bold=True)
        return 1
    
    for extension in extensions:
        if module := Extension.get_module(extension):
            try:
                module.initialize()
            except Exception as e:
                echo(f"Failed to initialize {extension} extension:", fg="red", bold=True)
                echo(str(e))
                return 1

    echo("Project initialized!", fg="green", bold=True)
    return 0


@main.command()
@option("--config", "-c", help="Path to the config file.", is_flag=False)
@argument("path", default=".", type=Path(exists=True))
def watch(config: str, path: str) -> int:
    """Starts a livereload server"""

    if enable("livereload", "livereload") != 0:
        return 1

    from livereload import Server

    server = Server()
    generator = Generator(path, config or 'config.ini')

    try:
        generator.copy_assets()
        generator.render_pages()

        for extension in generator.extensions:
            extension.render()
    except Exception as e:
        echo(f"Build failed:", fg="red", bold=True)
        echo(str(e))
        return 1

    server.watch(f"{generator.config.assets_path}/", generator.copy_assets)
    server.watch(f"{generator.config.pages_path}/", generator.render_pages)
    server.watch(f"{generator.config.templates_path}/", generator.render_pages)

    for extension in generator.extensions:
        for path in extension.to_watch:
            server.watch(path, extension.render)

    server.serve(root=generator.config.dist_path, port=generator.config.port, open_url_delay=0)
    return 0


@main.command()
@option("--config", "-c", help="Path to the config file.", is_flag=False)
@argument("path", default=".", type=Path(exists=True))
def build(config: str, path: str) -> int:
    """Build a Markdown-SPA project"""
    
    generator = echo_wrap(
        "Initializing generator",
        Generator, path, config or 'config.ini'
    )
    
    echo_wrap("Copying assets", generator.copy_assets)
    echo_wrap("Rendering pages", generator.render_pages)

    for extension in generator.extensions:
        echo_wrap(
            f"Running '{extension.name}' extension",
            extension.render
        )

    return 0
