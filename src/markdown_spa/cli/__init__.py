from .utils import echo
from .project import init, watch, build
from .extensions import install, uninstall, add

from click import group
from requests import get
from importlib_metadata import version


@group(context_settings=dict(help_option_names=['-h', '--help']))
def main_group() -> int:
    """Static site generator for Markdown files."""
    
    current = version("markdown-spa")
    latest = get("https://pypi.org/pypi/markdown-spa/json").json()

    if "info" in latest and latest["info"]["version"] > current:
        echo(f"Version {latest} is available, run 'pip install -U markdown-spa' to update.", fg="yellow", bold=True)

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