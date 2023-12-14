from requests import get
from os.path import exists
from subprocess import call, STDOUT
from importlib_metadata import version
from shutil import copytree, rmtree, move
from os import makedirs, chdir, devnull, remove

from .generator import Generator, echo, echo_wrap
from click import Path, Choice, group, option, argument, prompt


def check_version() -> None:
    current = version("markdown-spa")
    latest = get("https://pypi.org/pypi/markdown-spa/json").json()["info"]["version"]

    if latest > current:
        echo(f"Version {latest} is available, run 'pip install --U markdown-spa' to update.", fg="yellow", bold=True)

def silent_call(command: str) -> int:
    return call(command, shell=True, stdout=open(devnull, "w"), stderr=STDOUT)

def enable(import_name: str, package: str, ini: str = "") -> int:
    echo(f"Checking for {package}... ", nl=False)

    try:
        __import__(import_name)
        echo(f"found.", fg="green", bold=True)
        return 0
    except ImportError:
        echo(f"not found, installing it... ", nl=False)

    if silent_call(f"pip install {package}") != 0:
        echo(f"failed.", fg="red", bold=True)
        return 1
        
    echo(f"done.", fg="green", bold=True)
    return 0


@group()
def main() -> int:
    """Static site generator for Markdown files."""
    check_version()
    return 0


@main.command()
@argument("path", default=".")
def init(path: str) -> int:
    """Create a blank Markdown-SPA project."""

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

    styling = prompt(
        "Use pure CSS, SASS or TailwindCSS? (1, 2, 3)", type=Choice(["1", "2", "3"]),
        default="1", show_choices=False, show_default=False, prompt_suffix=" "
    )

    if styling in ("1", "3"):
        remove("assets/main.scss")
    if styling in ("1", "2"):
        remove("tailwind.config.js")

    if styling == "2":
        if enable("sass", "libsass") != 0:
            return 1

        source_path = prompt(
            "Enter the folder containing all SASS files (default: ./sass)",
            default="sass", prompt_suffix=": ", show_default=False
        )
        
        main_path = prompt(
            "Enter the main SASS file (default: main.scss)",
            default="main.scss", prompt_suffix=": ", show_default=False
        )

        remove("assets/style.css")
        makedirs(source_path, exist_ok=True)
        move("assets/main.scss", f"{source_path}/{main_path}")

        with open("config.ini", "a") as file:
            file.write(f"\n[SASS]\nsource_path = {source_path}\nmain_path = {source_path}/{main_path}\n")

    if styling == "3":
        if enable("pytailwindcss", "pytailwindcss") != 0:
            return 1

        input_file = prompt(
            "Enter the input file (default: assets/style.css)",
            default="assets/style.css", prompt_suffix=": ", show_default=False
        )

        config_file = prompt(
            "Enter the config file (default: tailwind.config.js)",
            default="tailwind.config.js", prompt_suffix=": ", show_default=False
        )

        move("assets/style.css", input_file)
        move("tailwind.config.js", config_file)

        with open(input_file, "r+") as file:
            content = file.read()
            file.seek(0, 0)
            file.write("@tailwind base;\n@tailwind components;\n@tailwind utilities;\n\n" + content)

        with open("config.ini", "a") as file:
            file.write(f"\n[TAILWIND]\ninput_file = {input_file}\nconfig_file = {config_file}\n")

    echo("Project initialized!", fg="green", bold=True)
    return 0


@main.command()
@option("--config", "-c", help="Path to the config file.", is_flag=False)
@argument("path", default=".", type=Path(exists=True))
def watch(config: str, path: str) -> int:
    """Starts a livereload server."""

    if enable("livereload", "livereload") != 0:
        return 1

    generator = echo_wrap(
        "Initializing generator",
        lambda: Generator(path, config or 'config.ini')
    )

    echo_wrap("Building project", generator.build, nl=True)

    from livereload import Server
    server = Server()

    server.watch(f"{generator.assets_path}/", generator.copy_assets)
    server.watch(f"{generator.pages_path}/", generator.render_pages)
    server.watch(f"{generator.templates_path}/", generator.render_pages)

    if "SASS" in generator.config:
        server.watch(f"{generator.root_path}/{generator.config['SASS']['source_path']}/", generator.build_sass)

    if "TAILWIND" in generator.config:
        server.watch(f"{generator.root_path}/{generator.config['TAILWIND']['input_file']}", generator.build_tailwind)

    server.serve(root=generator.dist_path, port=generator.port, open_url_delay=0)
    return 0


@main.command()
@option("--config", "-c", help="Path to the config file.", is_flag=False)
@argument("path", default=".", type=Path(exists=True))
def build(config: str, path: str) -> int:
    """Build the site."""
    
    gen = echo_wrap(
        "Building project",
        lambda: Generator(path, config or 'config.ini').build(), nl=True
    )

    return 0
