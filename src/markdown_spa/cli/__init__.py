from .project import init, watch, build
from .extensions import install, uninstall, add, list

from requests import get
from sys import executable
from importlib_metadata import version

from click import group, secho


@group(context_settings=dict(help_option_names=['-h', '--help']))
def main_group() -> int:
    """Static site generator for Markdown files."""
    
    current = version("markdown_spa")
    latest = get("https://pypi.org/pypi/markdown_spa/json").json()["info"]["version"]
    
    if latest > current:
        secho(f"Version {latest} is available, run '{executable} -m pip install -U markdown_spa' to update.", fg="yellow", bold=True)

    return 0

def main() -> None:
    """Create the main command group"""

    main_group.add_command(init)
    main_group.add_command(watch)
    main_group.add_command(build)
    main_group.add_command(install)
    main_group.add_command(uninstall)
    main_group.add_command(add)
    main_group.add_command(list)

    main_group()
