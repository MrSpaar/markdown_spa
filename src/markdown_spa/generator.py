from typing import TypedDict
from datetime import datetime
from os.path import exists, isdir
from shutil import copytree, rmtree
from configparser import ConfigParser
from os import environ, makedirs, listdir
from re import Match, compile as re_compile

from markdown import Markdown
from jinja2 import Environment, FileSystemLoader


class FileTree(TypedDict):
    path: str
    is_dir: bool
    meta: dict[str, str]
    children: list["FileTree"]


class Generator:
    PRE_RE = re_compile(r'<pre')
    TABLE_RE = re_compile(r'<table')
    CHECKBOX_RE = re_compile(r'\[([ xX])\] (.*)')
    INTERNAL_LINK_RE = re_compile(r'(href|src)="(/[^"]+|/)"')
    TAG_RE = re_compile(r'^[ ]{0,3}(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*)')

    def __init__(self, root_path: str = "", ini_path: str = "config.ini") -> None:
        self.config = ConfigParser()
        self.config.read(f"{root_path}/{ini_path}")

        self.port: int = self.config['GENERATOR'].getint('port')
        self.dist_path = f"{root_path}/{self.config['GENERATOR']['dist_path']}"
        self.pages_path = f"{root_path}/{self.config['GENERATOR']['pages_path']}"
        self.assets_path = f"{root_path}/{self.config['GENERATOR']['assets_path']}"
        self.templates_path = f"{root_path}/{self.config['GENERATOR']['templates_path']}"

        if not exists(self.dist_path):
            makedirs(self.dist_path, exist_ok=True)

        self.env = Environment(loader=FileSystemLoader(self.templates_path), auto_reload=True)
        self.md = Markdown(extensions=["meta", "tables", "attr_list", "fenced_code", "codehilite"])

        self.root_path = root_path
        self.url_root = f"http://localhost:{self.port}"    

        if "REPO" in environ:
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
            f.write(self.build_page(src_path,
                nav=self.nav, assets_path=self.assets_path[len(self.root_path)+1:], meta=tree["meta"])
            )
        
        for child in tree["children"]:
            self.__build(child)

    def build_page(self, path: str, **kwargs: object) -> str:
        with open(path) as f:
            content = f.read()

        content = Generator.CHECKBOX_RE.sub(
            Generator.__to_checkbox, self.md.convert(content)
        )

        content = Generator.PRE_RE.sub('<pre tabindex="0"', content)
        content = Generator.TABLE_RE.sub('<table tabindex="0"', content)
        
        return Generator.INTERNAL_LINK_RE.sub(
            rf'\1="{self.url_root}\2"',
            self.template.render(page_content=content, **kwargs)
        )

    def build_sass(self) -> None:
        from sass import compile as sass_compile

        with open(f"{self.dist_path}/{self.assets_path[len(self.root_path)+1:]}/style.css", "w") as f:
            f.write(sass_compile(
                filename=f"{self.root_path}/{self.config['SASS']['main_path']}",
                output_style="compressed",
            ))

    def build(self) -> None:
        self.tree = self.__prepare(self.pages_path)
        self.template = self.env.get_template("base.html")
        self.nav = self.env.get_template("nav.html").render(tree=self.tree)

        self.__build(self.tree)

        dist_assets_path = f"{self.dist_path}/{self.assets_path[len(self.root_path)+1:]}"
        if exists(dist_assets_path):
            rmtree(dist_assets_path)
        copytree(self.assets_path, dist_assets_path, dirs_exist_ok=True)
        
        if self.config["SASS"].getboolean("enabled"):
            self.build_sass()

        with open(f"{self.dist_path}/sitemap.xml", "w") as f:
            f.write(self.env.get_template("sitemap.xml").render(
                tree=self.tree, url=self.url_root,
                date=datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")
            ))

        with open(f"{self.dist_path}/robots.txt", "w") as f:
            f.write(self.env.get_template("robots.txt").render(url=self.url_root))
