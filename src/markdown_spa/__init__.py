from os.path import exists
from subprocess import call, STDOUT
from shutil import copytree, rmtree
from os import makedirs, chdir, devnull

from .generator import Generator
from click import Abort, Path, Choice, group, option, argument, echo, style, prompt


def silent_call(command: str) -> int:
    return call(command.split(" "), stdout=open(devnull, "w"), stderr=STDOUT)


def enable(import_name: str, package: str, update_ini=True) -> int:
    echo(style(f"Checking for {package}...", fg="yellow"))

    try:
        __import__(import_name)
        echo(style(f"{package} found.", fg="green"))
    except ImportError:
        echo(style(f"{package} not found, installing it...", fg="yellow"))

        if silent_call(f"pip install {package}") != 0:
            echo(style(f"Failed to install {package}.", fg="red", bold=True))
            return 1
        
        echo(style(f"{package} installed.", fg="green"))

    if update_ini:
        with open("config.ini", "r") as f:
            config = f.read().replace(f"[{package}]\nenabled = false", f"[{package}]\nenabled = true")
        
        with open("config.ini", "w") as f:
            f.write(config)

    return 0


@group()
def main() -> int:
    """Static site generator for Markdown files."""
    return 0


@main.command()
@argument("path", default=".")
def init(path: str) -> int:
    """Create a blank Markdown-SPA project."""

    if exists(path):
        echo(style("A file or directory with that name already exists!", fg="red", bold=True))
        return 1

    echo(style("Cloning blank project...", fg="yellow"))
    makedirs(path, exist_ok=True)
    chdir(path)

    commands = (
        "git init",
        "git remote add origin -f https://github.com/MrSpaar/Markdown-SPA.git",
        "git config core.sparseCheckout true",
        "echo 'blank' >> .git/info/sparse-checkout",
        "git pull origin master",
        "git remote remove origin"
    )

    for command in commands:
        if silent_call(command) != 0:
            echo(style("Failed to initialize project!", fg="red", bold=True))
            return 1

    try:
        styling = prompt(
            style("Use pure CSS, SASS or TailwindCSS? (1, 2, 3)", fg="yellow"),
            type=Choice(["1", "2", "3"]), default="1", show_choices=False, show_default=False, prompt_suffix=" "
        )
    except Abort:
        echo(style("Aborting...", fg="yellow"))
        rmtree("blank")
        return 1

    copytree("blank", ".", dirs_exist_ok=True)
    rmtree("blank")
    echo(style("Project cloned!", fg="green"))

    if styling == "2" and enable("sass", "libsass") != 0:
        return 1

    if styling == "3" and enable("pytailwindcss", "pytailwindcss") != 0:
        return 1

    echo(style("Project initialized!", fg="green"))
    return 0


@main.command()
@option("--config", "-c", help="Path to the config file.", is_flag=False)
@argument("path", default=".", type=Path(exists=True))
def build(config: str, path: str) -> int:
    """Build the site."""

    try:
        Generator(path, config or "config.ini").build()
        echo(style("Build complete!", fg="green"))
        return 0
    except Exception as e:
        echo(style(f"Build failed: {e}", fg="red", bold=True))
        return 1


@main.command()
@option("--config", "-c", help="Path to the config file.", is_flag=False)
@argument("path", default=".", type=Path(exists=True))
def watch(config: str, path: str) -> int:
    """Starts a livereload server."""

    if enable("livereload", "livereload", update_ini=False) != 0:
        return 1

    from livereload import Server

    generator = Generator(path, config or "config.ini")
    generator.build()

    server = Server()
    server.watch(f"{generator.pages_path}/", generator.build)
    server.watch(f"{generator.templates_path}/", generator.build)

    if generator.config["libsass"].getboolean("enabled"):
        server.watch(f"{generator.root_path}/{generator.config['libsass']['source_path']}/", generator.build_sass)

    if generator.config["pytailwindcss"].getboolean("enabled"):
        server.watch(f"{generator.root_path}/{generator.config['pytailwindcss']['input_file']}", generator.build_tailwind)

    server.serve(root=generator.dist_path, port=generator.port, open_url_delay=0)
    return 0
