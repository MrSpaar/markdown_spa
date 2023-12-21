from .utils import echo_wrap, echo, initialize_extension, silent_call

from shutil import rmtree
from os.path import exists
from sys import executable
from click import command, argument


@command()
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
        echo_wrap("Installing requirements", silent_call, f"{executable} -m pip install -r {name}/requirements.txt")
    
    echo("Extension installed!", fg="green", bold=True)
    return 0


@command()
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


@command()
@argument("name", type=str)
def add(name: str) -> int:
    """Add an extension to the project"""

    if not exists("./config.ini"):
        echo("No config.ini found!", fg="red", bold=True)
        return 1

    if err := initialize_extension(name):
        echo(err, fg="red", bold=True)
        return 1
    
    echo("Extension initialized!", fg="green", bold=True)
    
    return 0
