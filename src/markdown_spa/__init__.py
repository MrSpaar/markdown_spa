from shutil import copytree, rmtree
from os import makedirs, system, chdir

from .generator import Generator
from click import Path, BOOL, group, option, argument, echo, style


@group()
def main() -> int:
    """Static site generator for Markdown files."""
    return 0


@main.command()
@argument("path", default=".")
@option("--sass", "use_sass", help="Enable SASS suport.", prompt="Enable SASS suport? (Y/n) ", type=BOOL)
def init(path: str, use_sass: bool) -> int:
    """Create a blank Markdown-SPA project."""

    if use_sass:
        try:
            import sass
            echo(style("SASS found!", fg="green", bold=True))
        except ImportError:
            echo(style("SASS not found, installing it...", fg="yellow", bold=True))

            if system("pip install libsass") != 0:
                echo(style("Failed to install SASS!", fg="red", bold=True))
                return 1
            
            echo(style("SASS installed!", fg="green", bold=True))
            import sass

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


@main.command()
@option("--config", "-c", help="Path to the config file.", is_flag=False)
@argument("path", default=".", type=Path(exists=True))
def build(config: str, path: str) -> int:
    """Build the site."""

    try:
        Generator(path, config or "config.ini").build()
        echo(style("Build complete!", fg="green", bold=True))
        return 0
    except Exception as e:
        echo(style(f"Build failed: {e}", fg="red", bold=True))
        return 1


@main.command()
@option("--config", "-c", help="Path to the config file.", is_flag=False)
@argument("path", default=".", type=Path(exists=True))
def watch(config: str, path: str) -> int:
    """Starts a livereload server."""

    try:
        from livereload import Server
    except ImportError:
        echo(style("livereload not found, installing it...", fg="yellow", bold=True))

        if system("pip install livereload") != 0:
            echo(style("Failed to install livereload!", fg="red", bold=True))
            return 1
        
        echo(style("livereload installed!", fg="green", bold=True))
        from livereload import Server

    generator = Generator(path, config or "config.ini")
    generator.build()

    server = Server()
    server.watch(f"{generator.pages_path}/", generator.build)
    server.watch(f"{generator.templates_path}/", generator.build)

    if generator.config["SASS"].getboolean("enabled"):
        server.watch(f"{generator.root_path}/{generator.config['SASS']['source_path']}/", generator.build_sass)

    server.serve(root=generator.dist_path, port=generator.port, open_url_delay=0)
    return 0
