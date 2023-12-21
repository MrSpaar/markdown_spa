from .config import IniConfig
from .extension import Extension, get_extension

from os.path import isdir
from shutil import copytree
from os import makedirs, listdir
from typing import TypedDict, Optional
from re import Match, compile as re_compile

from markdown import Markdown
from jinja2 import Environment, FileSystemLoader


class Page(TypedDict):
    """Represents a markdown page"""

    meta: dict[str, str]
    children: dict[str, "Page"]


class Generator:
    """Generates the project"""

    QUOTE_RE = re_compile(r'> \[!([A-Z]+)\]')
    CHECKBOX_RE = re_compile(r'\[([ xX])\] (.*)')
    INTERNAL_LINK_RE = re_compile(r'(href|src)=["\'](/[^"\']+|/)["\']')
    TAG_RE = re_compile(r'^[ ]{0,3}(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*)')

    def __init__(self, root: str = "", ini_path: str = "config.ini") -> None:
        self.extensions: list[Extension] = []
        self.config = IniConfig(root, ini_path)

        self.md = Markdown(extensions=["extra", "codehilite", "meta"])
        self.env = Environment()

    @staticmethod
    def __to_checkbox(m: Match) -> str:
        checked: str = ' checked' if m.group(1).lower() == 'x' else ''
        return f"<input type='checkbox' disabled{checked} aria-label='checkbox list item'> {m.group(2)}"
    
    def __read_meta(self, path: str) -> dict[str, str]:
        meta: dict[str, str] = self.config.defaults()

        with open(path) as f:
            while (len(line := f.readline()) > 2 and (match := Generator.TAG_RE.match(line))):
                meta[match.group("key")] = match.group("value")
        
        return meta

    def __prepare(self, full_path: str) -> dict[str, Page] :
        entry: dict[str, Page] = {}

        for path in listdir(full_path):
            item_path = f"{full_path}/{path}"
            uri = item_path.removeprefix(f"{self.config.pages_path}/") \
                                .removesuffix(".md") \
                                .removeprefix("index")

            makedirs(f"{self.config.dist_path}/{uri}", exist_ok=True)

            if isdir(item_path) and uri in entry:
                entry[uri]["children"] = self.__prepare(item_path)
            elif isdir(item_path):
                entry[uri] = Page(
                    meta=self.config.defaults(),
                    children=self.__prepare(item_path)
                )
            elif uri in entry:
                entry[uri]["meta"] = self.__read_meta(item_path)
            else:
                entry[uri] = Page(meta=self.__read_meta(item_path), children={})
        
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

    def load_config(self) -> Optional[str]:
        """Loads config from config_path"""

        if error := self.config.load_config():
            return error
        
        for extension in self.config.extensions:
            instance = get_extension(extension)(self)

            if err := self.config.check_options(extension, instance.OPTIONS):
                return err

            self.extensions.append(instance)

        self.env.loader = FileSystemLoader(self.config.templates_path)

    def render_pages(self) -> Optional[str]:
        """Renders pages from pages_path to dist_path"""

        makedirs(self.config.dist_path, exist_ok=True)

        try:
            self.tree = self.__prepare(self.config.pages_path)
        except Exception as e:
            return f"Error while preparing pages: {e}"

        try:
            self.nav = self.env.get_template(self.config.nav_template).render(tree=self.tree)
        except Exception as e:
            return f"Error while rendering nav template: {e}"
        
        try:
            self.base_template = self.env.get_template(self.config.base_template)
            self.__render_tree(self.tree)
        except Exception as e:
            return f"Error while rendering pages: {e}"

    def copy_assets(self) -> Optional[str]:
        """Copies assets from assets_path to dist_assets_path"""

        try:
            copytree(self.config.assets_path, self.config.dist_assets_path, dirs_exist_ok=True)
        except Exception as e:
            return f"Error while copying assets: {e}"
