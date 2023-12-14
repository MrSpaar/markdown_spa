from datetime import datetime
from os.path import exists, isdir
from shutil import copytree, rmtree
from configparser import ConfigParser
from os import environ, makedirs, listdir
from re import Match, compile as re_compile
from typing import TypedDict, Callable, TypeVar

from markdown import Markdown
from click import style, echo as _echo
from jinja2 import Environment, FileSystemLoader


def echo(message: str, nl=True, **kwargs) -> None:
    _echo(style(message, **kwargs), nl=nl)

T = TypeVar("T")
def echo_wrap(message: str, func: Callable[..., T], *args, nl = False, indents=[0], **kwargs) -> T:
    echo(f"{' '*indents[0]}{message}... ", nl=nl)

    try:
        if nl:indents[0] += 4
        res = func(*args, **kwargs)

        if nl: indents[0] -= 4
        echo(f"done.", fg="green", bold=True)
        
        return res
    except Exception as e:
        if nl: indents[0] -= 4
        echo(f"failed.\nError: ", fg="red", bold=True, nl=False)
        echo(str(e))
        exit(1)


class Page(TypedDict):
    meta: dict[str, str]
    children: dict[str, "Page"]


class Generator:
    QUOTE_RE = re_compile(r'> \[!([A-Z]+)\]')
    CHECKBOX_RE = re_compile(r'\[([ xX])\] (.*)')
    INTERNAL_LINK_RE = re_compile(r'(href|src)=["\'](/[^"\']+|/)["\']')
    TAG_RE = re_compile(r'^[ ]{0,3}(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*)')

    def __init__(self, root_path: str = "", ini_path: str = "config.ini") -> None:
        self.config = ConfigParser()
        self.config.read(f"{root_path}/{ini_path}")

        if "GENERATOR" not in self.config:
            raise Exception("No 'GENERATOR' section in config.ini")
        
        gen_params = {"port", "dist_path", "pages_path", "assets_path", "templates_path"}
        if diff := gen_params.difference(self.config["GENERATOR"].keys()):
            raise Exception(f"Missing parameters in 'GENERATOR' section: {', '.join(diff)}")

        self.port: int = self.config['GENERATOR'].getint('port')
        self.dist_path = f"{root_path}/{self.config['GENERATOR']['dist_path']}"

        self.pages_path = f"{root_path}/{self.config['GENERATOR']['pages_path']}"
        if not exists(self.pages_path):
            raise Exception(f"Pages path '{self.pages_path}' does not exist")

        self.assets_path = f"{root_path}/{self.config['GENERATOR']['assets_path']}"
        if not exists(self.assets_path):
            raise Exception(f"Assets path '{self.assets_path}' does not exist")

        self.templates_path = f"{root_path}/{self.config['GENERATOR']['templates_path']}"
        if not exists(self.templates_path):
            raise Exception(f"Templates path '{self.templates_path}' does not exist")

        if not exists(f"{self.templates_path}/base.html"):
            raise Exception(f"Missing '{self.templates_path}/base.html' template")
        
        if not exists(f"{self.templates_path}/nav.html"):
            raise Exception(f"Missing '{self.templates_path}/nav.html' template")

        self.env = Environment(loader=FileSystemLoader(self.templates_path))
        self.md = Markdown(extensions=["meta", "tables", "attr_list", "fenced_code", "codehilite"])

        self.root_path = root_path
        self.url_root = f"http://localhost:{self.port}"    

        if "REPO" in environ:
            user, repo = environ["REPO"].split("/")
            self.url_root = f"https://{user}.github.io/{repo}"

    @staticmethod
    def __to_checkbox(match: Match) -> str:
        checked = match.group(1).lower() == 'x'
        return f"<input type='checkbox' disabled{' checked' if checked else ''} aria-label='checkbox list item'> {match.group(2)}"
    
    def __get_defaults(self) -> dict[str, str]:
        if not "DEFAULTS" not in self.config or not self.config["DEFAULTS"]:
            return {}
        return {**self.config["DEFAULTS"]}

    def __read_meta(self, path: str) -> dict[str, str]:
        meta: dict[str, str] = self.__get_defaults()

        with open(path) as f:
            while (len(line := f.readline()) > 2 and (match := Generator.TAG_RE.match(line))):
                meta[match.group("key")] = match.group("value")
        
        return meta

    def __prepare(self, full_path: str) -> dict[str, Page]:
        entry: dict[str, Page] = {}

        for path in listdir(full_path):
            item_path = f"{full_path}/{path}"
            uri = item_path.removeprefix(self.pages_path) \
                                .removeprefix("/") \
                                .removesuffix(".md") \
                                .removeprefix("index")

            makedirs(f"{self.dist_path}/{uri}", exist_ok=True)

            if isdir(item_path) and uri in entry:
                entry[uri]["children"] = self.__prepare(item_path)
            elif isdir(item_path):
                entry[uri] = Page(
                    meta=self.__get_defaults(),
                    children=self.__prepare(item_path)
                )
            elif uri in entry:
                entry[uri]["meta"] = self.__read_meta(item_path)
            else:
                entry[uri] = Page(meta=self.__read_meta(item_path), children={})
        
        return entry

    def __render_tree(self, tree: dict[str, Page]) -> None:
        for uri, page in tree.items():
            with open(f"{self.pages_path}/{uri or 'index'}.md") as f:
                content = self.md.convert(
                    Generator.QUOTE_RE.sub(r'> { .quote .quote-\1 }', f.read())
                )

            content = Generator.CHECKBOX_RE.sub(Generator.__to_checkbox, content) \
                                        .replace("<table", "<table tabindex='0'") \
                                        .replace("<pre", "<pre tabindex='0'")

            rendered = self.base_template.render(
                page_content=content, nav=self.nav, meta=page["meta"],
                assets_path=self.assets_path[self.assets_path.find("/")+1:]
            )

            with open(f"{self.dist_path}/{uri}/index.html", "w") as f:
                f.write(
                    Generator.INTERNAL_LINK_RE.sub(rf'\1="{self.url_root}\2"', rendered)
                )

            if page["children"]:
                self.__render_tree(page["children"])

    def render_pages(self) -> None:
        self.nav_template = self.env.get_template("nav.html")
        self.base_template = self.env.get_template("base.html")

        self.tree = echo_wrap(
            "Parsing file structure", 
            self.__prepare, self.pages_path
        )
        
        self.nav = echo_wrap(
            "Rendering nav", self.nav_template.render, tree=self.tree
        )

        makedirs(self.dist_path, exist_ok=True)
        echo_wrap("Building pages", self.__render_tree, tree=self.tree)

    def copy_assets(self) -> str:
        dist_assets_path = f"{self.dist_path}/{self.assets_path[len(self.root_path)+1:]}"
        copytree(self.assets_path, dist_assets_path, dirs_exist_ok=True)
        return dist_assets_path

    def build_sass(self, dist_assets_path: str = "") -> None:
        from sass import compile as sass_compile
        if not dist_assets_path:
            dist_assets_path = f"{self.dist_path}/{self.assets_path[len(self.root_path)+1:]}"

        sass_params = {"main_path", "source_path"}
        if diff := sass_params.difference(self.config["SASS"].keys()):
            raise Exception(f"Missing parameters in 'SASS' section: {', '.join(diff)}")

        main_path = f"{self.root_path}/{self.config['SASS']['main_path']}"
        if not exists(main_path):
            raise Exception(f"Main SASS file '{main_path}' does not exist")

        with open(f"{dist_assets_path}/style.css", "w") as f:
            f.write(sass_compile(
                filename=main_path,
                output_style="compressed",
            ))

    def build_tailwind(self, dist_assets_path: str = "") -> None:
        from pytailwindcss import run
        if not dist_assets_path:
            dist_assets_path = f"{self.dist_path}/{self.assets_path[len(self.root_path)+1:]}"

        tailwind_params = {"config_file", "input_file"}
        if diff := tailwind_params.difference(self.config["TAILWIND"].keys()):
            raise Exception(f"Missing parameters in 'TAILWIND' section: {', '.join(diff)}")

        config_path = f"{self.root_path}/{self.config['TAILWIND']['config_file']}"
        if not exists(config_path):
            raise Exception(f"Tailwind config file '{config_path}' does not exist")
        
        input_path = f"{self.root_path}/{self.config['TAILWIND']['input_file']}"
        if not exists(input_path):
            raise Exception(f"Tailwind input file '{input_path}' does not exist")

        run(f"-c {config_path} -i {input_path} -o {dist_assets_path}/style.css", auto_install=True)

    def render_seo(self) -> None:
        with open(f"{self.dist_path}/sitemap.xml", "w") as f:
            f.write(self.env.get_template("sitemap.xml").render(
                tree=self.tree, url=self.url_root,
                date=datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")
            ))

        with open(f"{self.dist_path}/robots.txt", "w") as f:
            f.write(self.env.get_template("robots.txt").render(url=self.url_root))

    def build(self) -> None:        
        self.render_pages()
        dist_assets_path = echo_wrap("Copying assets", self.copy_assets)

        if "SASS" in self.config:
            echo_wrap(
                "Building SASS",
                self.build_sass, dist_assets_path
            )
        
        if "TAILWIND" in self.config:
            echo_wrap(
                "Building Tailwind",
                self.build_tailwind, dist_assets_path
            )

        echo_wrap("Rendering SEO", self.render_seo)


if __name__ == "__main__":
    gen = echo_wrap(
        "Building project",
        lambda: Generator("doc/").build(), nl=True
    )
