from .generator import Generator
from ..extensions import Extension
from ..config import silent_call, ensure_lib

from pathlib import Path
from requests import get
from os.path import exists
from typing import Callable
from os import listdir, chdir
from shutil import copytree, rmtree
from importlib_metadata import version

from click import Path, group, option, argument, prompt, echo as _echo, style


def echo(message: str, nl=True, **kwargs) -> None:
    _echo(style(message, **kwargs), nl=nl)

def echo_wrap(message: str, func: Callable, *args, **kwargs) -> None:
    echo(f"{message}... ", nl=False)
    func(*args, **kwargs)
    echo(f"done", fg="green", bold=True)


@group(context_settings=dict(help_option_names=['-h', '--help']))
def main() -> int:
    """Static site generator for Markdown files."""
    
    current = version("markdown-spa")
    latest = get("https://pypi.org/pypi/markdown-spa/json").json()["info"]["version"]

    if latest > current:
        echo(f"Version {latest} is available, run 'pip install -U markdown-spa' to update.", fg="yellow", bold=True)

    return 0


@main.command()
@argument("name", type=str)
@argument("url", type=str)
def install(name: str, url: str) -> int:
    """Install an extension from a git repository"""

    if not url.endswith(".git"):
        echo("Invalid git repository URL!", fg="red", bold=True)
        return 1

    path = f"{__file__[:-7]}/../extensions/{name}"
    echo_wrap("Cloning repository", silent_call, f"git clone {url} {path}")

    if exists(f"{path}/requirements.txt"):
        echo_wrap("Installing requirements", silent_call, f"pip install -r {name}/requirements.txt")
    
    echo("Extension installed!", fg="green", bold=True)
    return 0


@main.command()
@argument("name", type=str)
def uninstall(name: str) -> int:
    """Uninstall an extension"""

    path = f"{__file__[:-7]}/../extensions/{name}"
    if not exists(path):
        echo("Extension not found!", fg="red", bold=True)
        return 1

    rmtree(path)
    echo("Extension removed!", fg="green", bold=True)
    return 0


@main.command()
@argument("name", type=str)
def add(name: str) -> int:
    """Add an extension to the project"""

    if not exists("./config.ini"):
        echo("No config.ini found!", fg="red", bold=True)
        return 1

    module = Extension.get_module(name)
    if not module:
        echo("Extension not found!", fg="red", bold=True)
        return 1
    
    module.initialize()
    echo("Extension initialized!", fg="green", bold=True)
    
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
            module.initialize()
        else:
            echo(f"Failed to load extension {extension}", fg="red", bold=True)
            return 1

    echo("Project initialized!", fg="green", bold=True)
    return 0


@main.command()
@option("--config", "-c", help="Path to the config file.", is_flag=False)
@argument("path", default=".", type=Path(exists=True))
def watch(config: str, path: str) -> int:
    """Starts a livereload server"""

    if not ensure_lib("livereload"):
        echo("Failed to install lib 'livereload'", fg="red", bold=True)
        return 1

    generator = Generator(path, config or 'config.ini')
    generator.build()

    from livereload import Server
    server = Server()

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
    
    echo_wrap(
        "Building project",
        Generator(path, config or 'config.ini').build
    )

    return 0
