from .utils import echo
from .project import init, watch, build
from .extensions import install, uninstall, add

from click import group
from requests import get
from sys import executable
from importlib_metadata import version


@group(context_settings=dict(help_option_names=['-h', '--help']))
def main_group() -> int:
    """Static site generator for Markdown files."""
    
    current = version("markdown-spa")

    try:
        latest = get("https://pypi.org/pypi/markdown-spa/json").json()["info"]["version"]
        if latest > current:
            echo(f"Version {latest} is available, run '{executable} -m pip install -U markdown-spa' to update.", fg="yellow", bold=True)
    except:
        pass

    return 0

def main() -> None:
    """Create the main command group"""

    main_group.add_command(init)
    main_group.add_command(watch)
    main_group.add_command(build)
    main_group.add_command(install)
    main_group.add_command(uninstall)
    main_group.add_command(add)

    main_group()
