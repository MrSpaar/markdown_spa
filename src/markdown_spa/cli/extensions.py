from .utils import echo_wrap, initialize_extension, silent_call

from os import listdir
from pathlib import Path
from shutil import rmtree
from os.path import exists
from sys import executable

from click import command, argument, secho


@command()
@argument("name", type=str)
@argument("url", type=str)
def install(name: str, url: str) -> int:
    """Install an extension from a git repository"""

    if not url.endswith(".git"):
        secho("Invalid git repository URL!", fg="red", bold=True)
        return 1

    path = f"{Path(__file__).parent.parent}/extensions/{name}"
    echo_wrap("Cloning repository", silent_call, f"git clone {url} {path}")

    if exists(f"{path}/requirements.txt"):
        echo_wrap("Installing requirements", silent_call, f"{executable} -m pip install -r {name}/requirements.txt")
    
    secho("Extension installed!", fg="green", bold=True)
    return 0


@command()
@argument("name", type=str)
def uninstall(name: str) -> int:
    """Uninstall an extension"""

    path = f"{Path(__file__).parent.parent}/extensions/{name}"
    if not exists(path):
        secho("Extension not found!", fg="red", bold=True)
        return 1

    rmtree(path)
    secho("Extension removed!", fg="green", bold=True)
    return 0


@command()
def list() -> int:
    """List installed extensions"""

    modules_path = f"{Path(__file__).parent.parent}/extensions"
    if not exists(modules_path):
        secho("No extensions found!", fg="red", bold=True)
        return 1

    extensions = [
        path for path in listdir(modules_path)
        if path not in ("__pycache__", "__init__.py") and exists (f"{modules_path}/{path}/__init__.py")
    ]

    if not extensions:
        secho("No extensions found!", fg="red", bold=True)
        return 1

    secho(f"Installed extensions: ", fg="green", bold=True, nl=False)
    secho(', '.join(extensions))

    return 0


@command()
@argument("name", type=str)
def add(name: str) -> int:
    """Add an extension to the project"""

    if not exists("./config.ini"):
        secho("No config.ini found!", fg="red", bold=True)
        return 1

    if err := initialize_extension(name):
        secho(err, fg="red", bold=True)
        return 1
    
    secho("Extension initialized!", fg="green", bold=True)
    return 0
