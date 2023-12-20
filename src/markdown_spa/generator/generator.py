from ..config import IniConfig
from ..extensions import Extension

from os.path import isdir
from shutil import copytree
from typing import TypedDict
from os import makedirs, listdir
from re import Match, compile as re_compile

from markdown import Markdown
from jinja2 import Environment, FileSystemLoader


class Generator:
    QUOTE_RE = re_compile(r'> \[!([A-Z]+)\]')
    CHECKBOX_RE = re_compile(r'\[([ xX])\] (.*)')
    INTERNAL_LINK_RE = re_compile(r'(href|src)=["\'](/[^"\']+|/)["\']')
    TAG_RE = re_compile(r'^[ ]{0,3}(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*)')

    class Page(TypedDict):
        meta: dict[str, str]
        children: dict[str, "Generator.Page"]

    def __init__(self, root: str = "", ini_path: str = "config.ini") -> None:
        self.extensions: list[Extension] = []
        self.config = IniConfig(root, ini_path)

        for name in set(self.config.sections()) - {"DEFAULTS", "GENERATOR"}:
            if not (module := Extension.get_module(name)):
                raise ImportError(f"Failed to load extension {name}")
            else:
                self.extensions.append(module(self))

        self.md = Markdown(extensions=["extra", "codehilite", "meta"])
        self.env = Environment(loader=FileSystemLoader(self.config.templates_path))

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
            uri = item_path.removeprefix(f"{self.config.pages_path}/") \
                                .removesuffix(".md") \
                                .removeprefix("index")

            makedirs(f"{self.config.dist_path}/{uri}", exist_ok=True)

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
            with open(f"{self.config.pages_path}/{uri or 'index'}.md") as f:
                content = self.md.convert(
                    Generator.QUOTE_RE.sub(r'> { .quote .quote-\1 }', f.read())
                )

            content = Generator.CHECKBOX_RE.sub(Generator.__to_checkbox, content) \
                                        .replace("<table", "<table tabindex='0'") \
                                        .replace("<pre", "<pre tabindex='0'")

            rendered = self.base_template.render(
                page_content=content, nav=self.nav, meta=page["meta"],
                assets_path=self.config.assets_path[self.config.assets_path.find("/")+1:]
            )

            with open(f"{self.config.dist_path}/{uri}/index.html", "w") as f:
                f.write(Generator.INTERNAL_LINK_RE.sub(rf'\1="{self.config.base_url}\2"', rendered))

            if page["children"]:
                self.__render_tree(page["children"])

    def render_pages(self) -> None:
        makedirs(self.config.dist_path, exist_ok=True)

        self.tree = self.__prepare(self.config.pages_path)
        self.nav = self.env.get_template("nav.html").render(tree=self.tree)

        self.base_template = self.env.get_template("base.html")
        self.__render_tree(self.tree)

    def copy_assets(self) -> None:
        copytree(self.config.assets_path, self.config.dist_assets_path, dirs_exist_ok=True)


    def build(self) -> None:
        self.copy_assets()
        self.render_pages()

        for extension in self.extensions:
            extension.render()
