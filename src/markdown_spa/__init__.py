from shutil import copytree, rmtree
from os import makedirs, system, chdir

from .generator import Generator
from click import Path, group, option, argument, echo, style


@group()
def main() -> int:
    """Static site generator for Markdown files."""
    return 0


@main.command()
@option("--config", "-c", help="Path to the config file.", is_flag=False)
@argument("path", default=".", type=Path(exists=True))
def watch(config, path) -> int:
    """Starts a livereload server."""

    try:
        from livereload import Server
    except ImportError:
        print("Livereload is not installed: `pip install livereload`")
        return 1

    generator = Generator(path, config or "config.ini")
    generator.build()

    server = Server()
    server.watch(f"{generator.pages_path}/", generator.build)
    server.watch(f"{generator.templates_path}/", generator.build)

    if generator.config["SASS"].getboolean("enabled"):
        server.watch(f"{generator.root_path}/{generator.config['SASS']['source_path']}/", generator.build_sass)

    server.serve(root=generator.dist_path, port=generator.port, open_url_delay=0)
    return 0


@main.command()
@option("--config", "-c", help="Path to the config file.", is_flag=False)
@argument("path", default=".", type=Path(exists=True))
def build(config, path) -> int:
    """Build the site."""

    try:
        Generator(path, config or "config.ini").build()
        echo(style("Build complete!", fg="green", bold=True))
        return 0
    except Exception as e:
        echo(style(f"Build failed: {e}", fg="red", bold=True))
        return 1


@main.command()
@argument("path", default=".")
def init(path) -> int:
    """Create a blank Markdown-SPA project."""

    makedirs(path, exist_ok=True)
    chdir(path)
    
    try:
        system("git init")
        system("git remote add origin -f https://github.com/MrSpaar/Markdown-SPA.git")
        system("git config core.sparseCheckout true")
        system("echo 'blank' >> .git/info/sparse-checkout")
        system("git pull origin master")
        system("git remote remove origin")
    except Exception as e:
        echo(style(f"Failed to initialize project: {e}", fg="red", bold=True))
        return 1

    copytree("blank", ".", dirs_exist_ok=True)
    rmtree("blank")

    echo(style("Project initialized!", fg="green", bold=True))
    return 0
