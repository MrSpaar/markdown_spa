from typing import TypedDict
from datetime import datetime
from os.path import exists, isdir
from configparser import ConfigParser
from re import Match, compile as re_compile
from os import environ, makedirs, system, listdir

from markdown import Markdown
from sass import compile as sass_compile
from jinja2 import Environment, FileSystemLoader


class FileTree(TypedDict):
    path: str
    is_dir: bool
    meta: dict[str, str]
    children: list["FileTree"]


class Generator:
    CHECKBOX_RE = re_compile(r'\[([ xX])\] (.*)')
    INTERNAL_LINK_RE = re_compile(r'(href|src)="(/[^"]+|/)"')
    TAG_RE = re_compile(r'^[ ]{0,3}(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*)')

    def __init__(self, ini_path: str) -> None:
        self.config = ConfigParser()
        self.config.read(ini_path)

        self.port = self.config["GENERATOR"].getint("port")
        self.scss_path = self.config["GENERATOR"]["scss_path"]
        self.dist_path = self.config["GENERATOR"]["dist_path"]
        self.pages_path = self.config["GENERATOR"]["pages_path"]
        self.assets_path = self.config["GENERATOR"]["assets_path"]
        self.templates_path = self.config["GENERATOR"]["templates_path"]

        if not exists(self.dist_path):
            makedirs(self.dist_path, exist_ok=True)

        self.env = Environment(loader=FileSystemLoader(self.templates_path), auto_reload=True)
        self.md = Markdown(extensions=["meta", "tables", "attr_list", "fenced_code", "codehilite"])

        self.in_gp = "REPO" in environ
        self.url_root = f"http://localhost:{self.port}"

        if self.in_gp:
            user, repo = environ["REPO"].split("/")
            self.url_root = f"https://{user}.github.io/{repo}"

    @staticmethod
    def __to_checkbox(match: Match) -> str:
        checked = match.group(1).lower() == 'x'
        return f"<input type='checkbox' disabled{' checked' if checked else ''} aria-label='Checkbox'> {match.group(2)}"

    def __prepare(self, full_path: str) -> FileTree:
        entry = FileTree(path=full_path.removeprefix(self.pages_path).removeprefix('/'), is_dir=True, meta={}, children=[])

        for path in listdir(full_path):
            if isdir(f"{full_path}/{path}"):
                entry["children"].append(self.__prepare(f"{full_path}/{path}"))
                continue

            is_index = path.endswith("index.md")
            item = entry if is_index else FileTree(
                path=f"{entry['path']}/{path[:-3]}".removeprefix("/"), is_dir=False, meta={}, children=[]
            )
            
            with open(f"{full_path}/{path}") as f:
                item["meta"] |= self.config["DEFAULTS"]

                while ((line := f.readline()) != "\n" and line != ""):
                    if match:= Generator.TAG_RE.match(line):
                        item["meta"][match.group("key")] = match.group("value")

            if not is_index:
                entry["children"].append(item)
        
        return entry

    def __build(self, tree: FileTree) -> None:
        makedirs(f"{self.dist_path}/{tree['path']}", exist_ok=True)

        if tree["is_dir"]:
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

    def link_assets(self) -> None:
        if not exists(f"{self.dist_path}/{self.assets_path}"):
            system(
                f"cp -r {self.assets_path} {self.dist_path}/" if self.in_gp
                else f"ln -s ../{self.assets_path} {self.dist_path}/"
            )

    def build_css(self) -> None:
        makedirs(f"{self.dist_path}/{self.assets_path}", exist_ok=True)

        with open(f"{self.dist_path}/{self.assets_path}/style.css", "w") as f:
            f.write(sass_compile(
                filename=self.scss_path,
                output_style="compressed",
            ))

    def build(self) -> None:
        self.tree = self.__prepare(self.pages_path)
        self.template = self.env.get_template("base.html")
        self.nav = self.env.get_template("nav.html").render(tree=self.tree)

        self.__build(self.tree)
        
        with open(f"{self.dist_path}/sitemap.xml", "w") as f:
            f.write(self.env.get_template("sitemap.xml").render(
                tree=self.tree, url=self.url_root, date=datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")
            ))

        with open(f"{self.dist_path}/robots.txt", "w") as f:
            f.write(self.env.get_template("robots.txt").render(url=self.url_root))


if __name__ == "__main__":
    gen = Generator("config.ini")

    gen.link_assets()
    gen.build_css()
    gen.build()

    print("Done!")
