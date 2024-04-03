from click import group

from .project import init, watch, build
from .extensions import install, uninstall, add, list


@group(context_settings=dict(help_option_names=['-h', '--help']))
def main_group() -> int:
    """Static site generator for Markdown files."""
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
