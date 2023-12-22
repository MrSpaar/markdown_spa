from ..generator import Generator, Dependency
from .utils import echo, initialize_extension, echo_wrap, ensure_installed, build_project


from os.path import exists
from shutil import copytree
from os import listdir, chdir
from pathlib import Path as PPath

from click import Path, command, option, argument, prompt


@command()
@argument("path", default=".")
def init(path: str) -> int:
    """Create a blank Markdown-SPA project"""

    if exists(path):
        echo("A file or directory with that name already exists!", fg="red", bold=True)
        return 1

    echo_wrap("Copying blank project... ", 
              copytree, PPath(__file__).parent/"blank", path, dirs_exist_ok=True)

    dirs = [
        path for path in listdir(PPath(__file__).parent.parent/"extensions")
        if not path.endswith(".py") and not path.startswith("__")
    ]
    
    dirs_str = "\n  - ".join(["", *dirs])
    inp = prompt(
        f"Choose extensions to enable (space-separated, empty to skip): {dirs_str}\n",
        type=str, prompt_suffix="> ", default="", show_default=False
    )

    if not inp:
        echo("Project initialized!", fg="green", bold=True)
        return 0

    extensions = inp.split(" ")
    if diff := set(extensions).difference(dirs):
        echo(f"Unknown extensions: {', '.join(diff)}", fg="red", bold=True)
        return 1
    
    chdir(path)
    for extension in extensions:
        if err := initialize_extension(extension):
            echo(err, fg="red", bold=True)
            return 1

    echo("Project initialized!", fg="green", bold=True)
    return 0


@command()
@option("--config", "-c", help="Path to the config file.", is_flag=False)
@argument("path", default=".", type=Path(exists=True))
def watch(config: str, path: str) -> int:
    """Starts a livereload server"""

    if err := ensure_installed(Dependency("livereload")):
        echo(err)
        echo("Failed to install livereload!", fg="red", bold=True)
        return 1

    generator = Generator(path, config or 'config.ini')
    if build_project(generator) != 0:
        return 1

    from livereload import Server
    server = Server()

    server.watch(f"{generator.config.assets_path}/", generator.copy_assets)
    server.watch(f"{generator.config.pages_path}/", generator.render_pages)
    server.watch(f"{generator.config.templates_path}/", generator.render_pages)

    for extension in generator.extensions:
        for path in extension.TO_WATCH:
            server.watch(path, extension.render)

    server.serve(root=generator.config.dist_path, port=generator.config.port, open_url_delay=0)
    return 0


@command()
@option("--config", "-c", help="Path to the config file.", is_flag=False)
@argument("path", default=".", type=Path(exists=True))
def build(config: str, path: str) -> int:
    """Build a Markdown-SPA project"""
    return build_project(Generator(path, config or 'config.ini'))