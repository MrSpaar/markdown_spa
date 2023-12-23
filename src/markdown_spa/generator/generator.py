from .config import IniConfig
from .extension import Extension, get_extension

from os.path import isdir
from shutil import copytree
from os import makedirs, listdir
from re import Match, compile as re_compile
from typing import TypedDict, Optional, Union, Literal

from markdown import Markdown
from jinja2 import Environment, FileSystemLoader, Template


class Page(TypedDict):
    """Represents a markdown page"""

    meta: dict[str, str]
    children: dict[str, "Page"]
    ext: Union[Literal["md"], Literal["html"]]


class Generator:
    """Main class for building `markdown_spa` projects"""

    QUOTE_RE = re_compile(r'> \[!([A-Z]+)\]')
    CHECKBOX_RE = re_compile(r'\[([ xX])\] (.*)')
    INTERNAL_LINK_RE = re_compile(r'(href|src)=["\'](/[^"\']+|/)["\']')
    TAG_RE = re_compile(r'^[ ]{0,3}(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*)')

    def __init__(self, root: str = "", ini_path: str = "config.ini") -> None:
        self.extensions: list[Extension] = []
        self.config = IniConfig(root, ini_path)

        self.env = Environment()
        self.md = Markdown(extensions=["extra", "codehilite"])

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

    def __prepare(self, full_path: str) -> dict[str, Page]:
        entry: dict[str, Page] = {}

        for path in listdir(full_path):
            item_path = f"{full_path}/{path}"
            ext = item_path[item_path.rfind(".")+1:]

            uri = item_path.removeprefix(f"{self.config.pages_path}/") \
                                .removesuffix(f".{ext}") \
                                .removesuffix("index")

            if isdir(item_path) and uri in entry:
                entry[uri]["children"] = self.__prepare(item_path)
                continue

            if uri in entry:
                entry[uri]["meta"] = self.__read_meta(item_path)
                continue

            if not isdir(item_path) and ext in ("html", "md"):
                entry[uri] = Page(meta=self.__read_meta(item_path), ext=ext, children={})
                continue

            entry[uri] = Page(
                ext="md",
                meta=self.config.defaults(),
                children=self.__prepare(item_path)
            )
        
        return entry

    def __render_tree(self, tree: dict[str, Page]) -> None:
        for uri, page in tree.items():
            makedirs(f"{self.config.dist_path}/{uri}", exist_ok=True)

            with open(f"{self.config.pages_path}/{uri or 'index'}.{page['ext']}") as f:
                for _ in range(len(page["meta"].keys())):
                    f.readline()
                content = f.read()

            if page["ext"] == "html":
                with open(f"{self.config.dist_path}/{uri}/index.html", "w") as f:
                    f.write(Template(content).render(
                        nav=self.nav, meta=page["meta"],
                        assets_path=self.config.assets_path[self.config.assets_path.find("/")+1:]
                    ))
                
                continue

            content = self.md.convert(
                Generator.QUOTE_RE.sub(r'> { .quote .quote-\1 }', content)
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
