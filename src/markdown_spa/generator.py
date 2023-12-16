from shutil import copytree
from datetime import datetime
from os.path import exists, isdir
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


class Generator:
    QUOTE_RE = re_compile(r'> \[!([A-Z]+)\]')
    CHECKBOX_RE = re_compile(r'\[([ xX])\] (.*)')
    INTERNAL_LINK_RE = re_compile(r'(href|src)=["\'](/[^"\']+|/)["\']')
    TAG_RE = re_compile(r'^[ ]{0,3}(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*)')

    class Page(TypedDict):
        meta: dict[str, str]
        children: dict[str, "Generator.Page"]

    __slots__ = ("config", "port",
        "dist_path", "pages_path", "assets_path", "templates_path", "dist_assets_path",
        "env", "md", "root_path", "url_root", "nav_template", "base_template", "tree", "nav",
        "SASS_main_path", "SASS_source_path", "TAILWIND_config_file", "TAILWIND_input_file", 
    )

    def __init__(self, root_path: str = "", ini_path: str = "config.ini") -> None:
        if not exists(f"{root_path}/{ini_path}"):
            raise Exception(f"Missing '{root_path}/{ini_path}' config file")

        self.config = ConfigParser()
        self.config.read(f"{root_path}/{ini_path}")

        if "GENERATOR" not in self.config:
            raise Exception("No 'GENERATOR' section in config.ini")

        if "port" not in self.config["GENERATOR"]:
            raise Exception("Missing 'port' parameter in 'GENERATOR' section")

        for param in ("dist_path", "pages_path", "assets_path", "templates_path"):
            if param not in self.config["GENERATOR"]:
                raise Exception(f"Missing '{param}' parameter in 'GENERATOR' section")

            setattr(self, param, f"{root_path}/{self.config['GENERATOR'][param]}")
        
        if not exists(f"{self.templates_path}/base.html"):
            raise Exception(f"Missing '{self.templates_path}/base.html' template")

        if not exists(f"{self.templates_path}/nav.html"):
            raise Exception(f"Missing '{self.templates_path}/nav.html' template")

        for section, params in ("TAILWIND", ("config_file", "input_file")), ("SASS", ("main_path", "source_path")):
            if section in self.config:
                for param in params:
                    if param not in self.config[section]:
                        raise Exception(f"Missing '{param}' parameter in '{section}' section")

                    if not exists(f"{root_path}/{self.config[section][param]}"):
                        raise Exception(f"Missing '{root_path}/{self.config[section][param]}' file")
                
                    setattr(self, f"{section}_{param}", f"{root_path}/{self.config[section][param]}")

        self.root_path = root_path
        self.port: int = self.config['GENERATOR'].getint('port')
        self.url_root = f"http://localhost:{self.port}"

        if "REPO" in environ:
            user, repo = environ["REPO"].split("/")
            self.url_root = f"https://{user}.github.io/{repo}"

        self.env = Environment(loader=FileSystemLoader(self.templates_path))
        self.md = Markdown(extensions=["meta", "tables", "attr_list", "fenced_code", "codehilite"])   
        self.dist_assets_path = f"{self.dist_path}/{self.assets_path[len(self.root_path)+1:]}"

    @staticmethod
    def __to_checkbox(m: Match) -> str:
        checked: str = ' checked' if m.group(1).lower() == 'x' else ''
        return f"<input type='checkbox' disabled{checked} aria-label='checkbox list item'> {m.group(2)}"
    
    def __get_defaults(self) -> dict[str, str]:
        return {**self.config["DEFAULTS"]} if self.config.has_section("DEFAULTS") else {}

    def __read_meta(self, path: str) -> dict[str, str]:
        meta: dict[str, str] = self.__get_defaults()

        with open(path) as f:
            while (len(line := f.readline()) > 2 and (match := Generator.TAG_RE.match(line))):
                meta[match.group("key")] = match.group("value")
        
        return meta

    def __prepare(self, full_path: str) -> dict[str, Page]:
        entry: dict[str, Generator.Page] = {}

        for path in listdir(full_path):
            item_path = f"{full_path}/{path}"
            uri = item_path.removeprefix(f"{self.pages_path}/") \
                                .removesuffix(".md") \
                                .removeprefix("index")

            makedirs(f"{self.dist_path}/{uri}", exist_ok=True)

            if isdir(item_path) and uri in entry:
                entry[uri]["children"] = self.__prepare(item_path)
            elif isdir(item_path):
                entry[uri] = Generator.Page(
                    meta=self.__get_defaults(),
                    children=self.__prepare(item_path)
                )
            elif uri in entry:
                entry[uri]["meta"] = self.__read_meta(item_path)
            else:
                entry[uri] = Generator.Page(meta=self.__read_meta(item_path), children={})
        
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
                f.write(Generator.INTERNAL_LINK_RE.sub(rf'\1="{self.url_root}\2"', rendered))

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

    def copy_assets(self) -> None:
        copytree(self.assets_path, self.dist_assets_path, dirs_exist_ok=True)

    def build_sass(self) -> None:
        from sass import compile as sass_compile

        with open(f"{self.dist_assets_path}/style.css", "w") as f:
            f.write(sass_compile(filename=self.SASS_main_path, output_style="compressed"))

    def build_tailwind(self) -> None:
        from pytailwindcss import run

        run(auto_install=True, tailwindcss_cli_args=
            f"-c {self.TAILWIND_config_file} -i {self.TAILWIND_input_file} -o {self.dist_assets_path}/style.css"
        )

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
        echo_wrap("Copying assets", self.copy_assets)

        if "SASS" in self.config:
            echo_wrap("Building SASS", self.build_sass)
        
        if "TAILWIND" in self.config:
            echo_wrap("Building Tailwind", self.build_tailwind)

        echo_wrap("Rendering SEO", self.render_seo)


if __name__ == "__main__":
    gen = echo_wrap(
        "Initializing generator",
        lambda: Generator("doc/")
    )

    echo_wrap("Building", gen.build, nl=True)
