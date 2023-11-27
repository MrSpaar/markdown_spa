from typing import TypedDict
from re import Match, compile
from os.path import exists, isdir
from configparser import ConfigParser
from os import environ, makedirs, system, listdir

from markdown import Markdown
from jinja2 import Environment, FileSystemLoader


class FileTree(TypedDict):
    path: str
    meta: dict[str, str]
    children: list["FileTree"]


class Generator:
    CHECKBOX_RE = compile(r'\[([ xX])\] (.*)')
    INTERNAL_LINK_RE = compile(r'(href|src)="(/[^"]+|/)"')
    TAG_RE = compile(r'^[ ]{0,3}(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*)')

    def __init__(self, ini_path: str) -> None:
        self.config = ConfigParser()
        self.config.read(ini_path)

        self.dist_path = self.config["GENERATOR"]["dist_path"]
        self.pages_path = self.config["GENERATOR"]["pages_path"]
        self.assets_path = self.config["GENERATOR"]["assets_path"]
        self.templates_path = self.config["GENERATOR"]["templates_path"]

        if not exists(self.dist_path):
            makedirs(self.dist_path, exist_ok=True)

        self.env = Environment(loader=FileSystemLoader(self.templates_path))
        self.template = self.env.get_template("base.html")
        self.md = Markdown(extensions=["meta", "tables", "attr_list", "fenced_code", "codehilite"])

        self.url_root = self.config["GENERATOR"]["url_root"]
        self.in_gp = "URL_ROOT" in environ

        if self.in_gp:
            self.url_root = f"/{environ['URL_ROOT'].split('/')[1]}"

    @staticmethod
    def __to_checkbox(match: Match) -> str:
        checked = match.group(1).lower() == 'x'
        return f"<input type='checkbox' disabled{' checked' if checked else ''}> {match.group(2)}"

    def __prepare(self, full_path: str) -> FileTree:
        entry = FileTree(path=full_path.removeprefix(self.pages_path).removeprefix('/'), meta={}, children=[])

        for path in listdir(full_path):
            if isdir(f"{full_path}/{path}"):
                entry["children"].append(self.__prepare(f"{full_path}/{path}"))
                continue

            is_index = path.endswith("index.md")
            item = entry if is_index else FileTree(path=f"{entry['path']}/{path[:-3]}", meta={}, children=[])
            
            with open(f"{full_path}/{path}") as f:
                while ((line := f.readline()) != "\n"):
                    if match:= Generator.TAG_RE.match(line):
                        item["meta"][match.group("key")] = match.group("value")

            if not is_index:
                entry["children"].append(item)
        
        return entry

    def __build_nav(self, tree: FileTree) -> None:
        self.nav = self.env.get_template("nav.html").render(tree=tree)

    def __build(self, tree: FileTree) -> None:
        makedirs(f"{self.dist_path}/{tree['path']}", exist_ok=True)

        if tree["children"]:
            src_path = f"{self.pages_path}/{tree['path']}/index.md"
            dist_path = f"{self.dist_path}/{tree['path']}/index.html"
        else:
            src_path = f"{self.pages_path}/{tree['path']}.md"
            dist_path = f"{self.dist_path}/{tree['path']}/index.html"

        with open(dist_path, "w") as f:
            f.write(self.build_page(src_path, nav=self.nav, assets_path=self.assets_path, meta=tree["meta"]))
        
        for child in tree["children"]:
            self.__build(child)

    def build_page(self, path: str, **kwargs: object) -> str:
        with open(path) as f:
            content = f.read()

        content = Generator.CHECKBOX_RE.sub(
            Generator.__to_checkbox, self.md.convert(content)
        )
        
        return Generator.INTERNAL_LINK_RE.sub(
            rf'\1="{self.url_root}\2"',
            self.template.render(page_content=content, **kwargs)
        )
    
    def build(self) -> None:
        self.tree = self.__prepare(self.pages_path)

        if not exists(f"{self.dist_path}/{self.assets_path}"):
            system(
                f"cp -r {self.assets_path} {self.dist_path}/" if self.in_gp
                else f"ln -s ../{self.assets_path} {self.dist_path}/"
            )

        self.__build_nav(self.tree)
        self.__build(self.tree)

        print("Build complete!")
    
    @staticmethod
    def build_from_ini(ini_path: str) -> None:
        Generator(ini_path).build()


if __name__ == "__main__":
    Generator.build_from_ini("config.ini")
