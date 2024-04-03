from os import listdir
from pathlib import Path
from shutil import rmtree
from os.path import exists
from sys import executable

from click import command, argument, option, secho
from .utils import echo_wrap, initialize_extension, call


@command()
@option("--full-trackback", "-ft", is_flag=True, help="Show full trackback on error", default=False)
@option("--upgrade", "-U", is_flag=True, help="Upgrade or install an extension", default=False)
@argument("name", type=str)
@argument("url", type=str)
def install(full_traceback: bool, upgrade: bool, name: str, url: str) -> int:
    """Install an extension from a git repository"""

    if not url.endswith(".git"):
        secho("Invalid git repository URL!", fg="red", bold=True)
        return 1

    path = f"{Path(__file__).parent.parent}/extensions/{name}"

    if upgrade and exists(path) and (
        err := echo_wrap("Updating repository", call, f"git -C {path} pull", full_tb=full_traceback)
    ):
        secho(err, fg="red", bold=True)
        return 1

    if not upgrade and (
        err := echo_wrap("Cloning repository", call, f"git clone {url} {path}", full_tb=full_traceback)
    ):
        secho(err, fg="red", bold=True)
        return 1

    if exists(f"{path}/requirements.txt") and (
        err := echo_wrap("Installing requirements", call, f"{executable} -m pip install -r {name}/requirements.txt", full_tb=full_traceback)
    ):
        secho(err, fg="red", bold=True)
        return 1

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
        if path not in ("__pycache__", "__init__.py") and exists(f"{modules_path}/{path}/__init__.py")
    ]

    if not extensions:
        secho("No extensions found!", fg="red", bold=True)
        return 1

    secho("Installed extensions: ", fg="green", bold=True, nl=False)
    secho(', '.join(extensions))

    return 0


@command()
@option("--full-traceback", "-ft", help="Show full traceback on error.", is_flag=True, default=False)
@argument("name", type=str)
def add(full_traceback: bool, name: str) -> int:
    """Add an extension to the project"""

    if not exists("./config.ini"):
        secho("No config.ini found!", fg="red", bold=True)
        return 1

    if err := initialize_extension(name, full_traceback):
        secho(err, fg="red", bold=True)
        return 1

    secho("Extension initialized!", fg="green", bold=True)
    return 0
