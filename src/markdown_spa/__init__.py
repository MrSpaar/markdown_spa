from os.path import exists
from subprocess import call, STDOUT
from shutil import copytree, rmtree
from os import makedirs, chdir, devnull

from .generator import Generator
from click import Path, Choice, group, option, argument, prompt, style, echo as _echo


def silent_call(command: str) -> int:
    return call(command.split(" "), stdout=open(devnull, "w"), stderr=STDOUT)

def echo(message: str, nl=True, **kwargs) -> None:
    _echo(style(message, **kwargs), nl=nl)


def enable(import_name: str, package: str, ini: str = "") -> int:
    echo(f"Checking for {package}... ", nl=False)

    try:
        __import__(import_name)
        echo(f"found.", fg="green", bold=True)
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
    return 0


@main.command()
@argument("path", default=".")
def init(path: str) -> int:
    """Create a blank Markdown-SPA project."""

    if exists(path):
        echo("A file or directory with that name already exists!", fg="red", bold=True)
        return 1

    echo("Cloning blank project... ", nl=False)
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
            echo("failed.", fg="red", bold=True)
            return 1

    copytree("blank", ".", dirs_exist_ok=True)
    rmtree("blank")
    echo("done.", fg="green", bold=True)

    styling = prompt(
        "Use pure CSS, SASS or TailwindCSS? (1, 2, 3)", type=Choice(["1", "2", "3"]),
        default="1", show_choices=False, show_default=False, prompt_suffix=" "
    )

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

        try:
            makedirs(source_path, exist_ok=True)
            open(f"{source_path}/{main_path}", "w").close()
        except Exception as e:
            echo(f"Failed to create SASS files.\nCause: ", fg="red", bold=True, nl=False)
            echo(str(e))
            return 1

        with open("config.ini", "a") as file:
            file.write(f"\n[SASS]\nsource_path = {source_path}\nmain_path = {main_path}\n")

    if styling == "3":
        if enable("pytailwindcss", "pytailwindcss") != 0:
            return 1

        input_file = prompt(
            "Enter the input file (default: tailwind.css)",
            default="tailwind.css", prompt_suffix=": ", show_default=False
        )

        output_file = prompt(
            "Enter the output file (default: style.css)",
            default="style.css", prompt_suffix=": ", show_default=False
        )

        config_file = prompt(
            "Enter the config file (default: tailwind.config.js)",
            default="tailwind.config.js", prompt_suffix=": ", show_default=False
        )

        try:
            for file in (input_file, output_file, config_file):
                makedirs(f"{file[:file.rfind('/')]}", exist_ok=True)
                open(file, "w").close()
        except Exception as e:
            echo(f"Failed to create TailwindCSS files.\nCause: ", fg="red", bold=True, nl=False)
            echo(str(e))
            return 1

        with open(input_file, "w") as file:
            file.write("@tailwind base;\n@tailwind components;\n@tailwind utilities;\n\n")

        with open("config.ini", "a") as file:
            file.write(f"\n[TAILWIND]\ninput_file = {input_file}\noutput_file = {output_file}\nconfig_file = {config_file}\n")

    echo("Project initialized!", fg="green", bold=True)
    return 0


@main.command()
@option("--config", "-c", help="Path to the config file.", is_flag=False)
@argument("path", default=".", type=Path(exists=True))
def build(config: str, path: str) -> int:
    """Build the site."""
    echo("Building site... ", nl=False)

    try:
        Generator(path, config or "config.ini").build()
        echo("done.", fg="green", bold=True)
        return 0
    except Exception as e:
        echo(f"failed.\nCause: ", fg="red", bold=True, nl=False)
        echo(str(e))
        return 1


@main.command()
@option("--config", "-c", help="Path to the config file.", is_flag=False)
@argument("path", default=".", type=Path(exists=True))
def watch(config: str, path: str) -> int:
    """Starts a livereload server."""

    if enable("livereload", "livereload") != 0:
        return 1

    from livereload import Server
    echo("Building site... ", nl=False)

    try:
        generator = Generator(path, config or "config.ini")
        generator.build()
    except Exception as e:
        echo(f"failed.\nCause: ", fg="red", bold=True, nl=False)
        echo(str(e))
        return 1

    echo("done.", fg="green", bold=True)
    server = Server()

    server.watch(f"{generator.pages_path}/", generator.build)
    server.watch(f"{generator.templates_path}/", generator.build)

    if "SASS" in generator.config:
        server.watch(f"{generator.root_path}/{generator.config['SASS']['source_path']}/", generator.build_sass)

    if "TAILWIND" in generator.config:
        server.watch(f"{generator.root_path}/{generator.config['TAILWIND']['input_file']}", generator.build_tailwind)

    server.serve(root=generator.dist_path, port=generator.port, open_url_delay=0)
    return 0
