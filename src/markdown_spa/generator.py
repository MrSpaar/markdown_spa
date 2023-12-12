from typing import TypedDict
from datetime import datetime
from os.path import exists, isdir
from shutil import copytree, rmtree
from configparser import ConfigParser
from re import Match, compile as re_compile
from os import environ, makedirs, listdir, system

from markdown import Markdown
from jinja2 import Environment, FileSystemLoader


class Page(TypedDict):
    meta: dict[str, str]
    children: dict[str, "Page"]


class Generator:
    PRE_RE = re_compile(r'<pre')
    TABLE_RE = re_compile(r'<table')
    QUOTE_RE = re_compile(r'> \[!([A-Z]+)\]')
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
        return f"<input type='checkbox' disabled{' checked' if checked else ''} aria-label='checkbox list item'> {match.group(2)}"
    
    def __read_meta(self, path: str) -> dict[str, str]:
        meta: dict[str, str] = {**self.config["DEFAULTS"]}

        with open(path) as f:
            while (len(line := f.readline()) > 2):
                if match := Generator.TAG_RE.match(line):
                    meta[match.group("key")] = match.group("value")
                else:
                    break
        
        return meta

    def __prepare(self, full_path: str) -> dict[str, Page]:
        entry: dict[str, Page] = {}

        for path in listdir(full_path):
            item_path = f"{full_path}/{path}"
            uri = item_path.removeprefix(self.pages_path) \
                            .removeprefix("/") \
                            .removesuffix(".md") \
                            .removeprefix("index")

            if isdir(item_path) and uri in entry:
                entry[uri]["children"] = self.__prepare(item_path)
            elif isdir(item_path):
                entry[uri] = Page(
                    meta={**self.config["DEFAULTS"]},
                    children=self.__prepare(item_path)
                )
            elif uri in entry:
                entry[uri]["meta"] = self.__read_meta(item_path)
            else:
                entry[uri] = Page(meta=self.__read_meta(item_path), children={})
        
        return entry

    def __build(self, tree: dict[str, Page]) -> None:
        for uri, page in tree.items():
            makedirs(f"{self.dist_path}/{uri}", exist_ok=True)

            with open(f"{self.pages_path}/{uri or 'index'}.md") as f:
                content = Generator.QUOTE_RE.sub(
                r'> { .quote .quote-\1 }', f.read()
                )

            content = Generator.CHECKBOX_RE.sub(
                Generator.__to_checkbox, self.md.convert(content)
            )

            content = Generator.PRE_RE.sub('<pre tabindex="0"', content)
            content = Generator.TABLE_RE.sub('<table tabindex="0"', content)
            
            with open(f"{self.dist_path}/{uri}/index.html", "w") as f:
                f.write(Generator.INTERNAL_LINK_RE.sub(
                rf'\1="{self.url_root}\2"',
                self.template.render(
                    page_content=content,
                    nav=self.nav,
                    meta=page["meta"],
                    assets_path=self.assets_path[self.assets_path.find("/")+1:]
                )
            ))

            if page["children"]:
                self.__build(page["children"])

    def build_sass(self) -> None:
        try:
            import sass
        except ImportError:
            system("pip install libsass")
            
        from sass import compile as sass_compile

        with open(f"{self.dist_path}/{self.assets_path[len(self.root_path)+1:]}/style.css", "w") as f:
            f.write(sass_compile(
                filename=f"{self.root_path}/{self.config['SASS']['main_path']}",
                output_style="compressed",
            ))

    def build(self) -> None:
        self.tree = self.__prepare(self.pages_path)
        self.nav = self.env.get_template("nav.html").render(tree=self.tree)

        self.template = self.env.get_template("base.html")
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

if __name__ == "__main__":
    Generator("doc").build()
    print("Done!")
