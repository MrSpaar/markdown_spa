from json import dump
from string import Template
from markdown import markdown
from os import listdir, path, makedirs, mkdir, environ, system

NestedDict = dict[str, "str | NestedDict"]


class Generator:
    def __init__(self, src: str, dist: str, templates: str, assets: str) -> None:
        if not path.exists(dist):
            makedirs(dist, exist_ok=True)
            mkdir(f"{dist}/pages")

        self.dist = dist
        self.assets = assets
        self.url_root = ""
        self.templates: dict[str, Template] = {}
        self.structure: NestedDict = self.render_pages(src, f"{dist}/pages")

        if 'URL_ROOT' in environ:
            self.url_root = f"/{environ['URL_ROOT'].split('/')[1]}"

        with open(f"{dist}/structure.json", "w") as f:
            dump(self.structure, f, indent=4)

        for file in listdir(templates):
            with open(templates+"/"+file, "r") as f:
                self.templates[file] = Template(f.read())

    def render_pages(self, src_root: str, dist_root: str):
        src_root += "/"
        dist_root += "/"
        structure: NestedDict = {}

        for page in listdir(src_root):
            new_src = src_root + page
            new_dist = dist_root + page.replace(".md", ".html")

            if (path.isdir(new_src)):
                if not path.exists(new_dist):
                    makedirs(new_dist, exist_ok=True)
            
                structure[page] = self.render_pages(new_src, new_dist)
                continue

            filename = page.removesuffix(".md")
            structure[filename] = filename.title()

            with open(new_src, "r") as f:
                with open(new_dist, "w") as b:
                    b.write(markdown(f.read(), extensions=["fenced_code"]))
            
        return structure

    def render_template(self, name: str, indents: int = 0, **kwargs: object) -> str:
        if name not in self.templates:
            raise Exception(f"Template {name} not found")

        return "\n".join(" "*indents + line
                         for line in self.templates[name].substitute(**kwargs).split("\n"))

    def _render_nav(self, parent: NestedDict, full_path: str, indents: int, first: bool = False) -> str:
        nav: str = ""
        indents = 4 if first else indents

        for path, item in parent.items():
            if isinstance(item, str):
                nav += self.render_template(
                    "item.html", indents, uri=f"{full_path}{path}", title=item
                )
                continue

            nav += self.render_template(
                "category.html", indents+8, title=path.title(),
                element=self._render_nav(item, full_path+path+"/", indents)
            )
        
        return nav
    
    def render_nav(self, indents: int) -> str:
        full_path = f"{self.url_root}/pages/"
        return self._render_nav(self.structure, full_path, indents, True)
    
    def render_index(self, indents: int) -> None:
        html = self.render_template(
            "index.html", 0,
            nav=self.render_nav(indents+4), url_root=self.url_root
        )

        with open(f"{self.dist}/index.html", "w") as f:
            f.write(html)

    def link_assets(self) -> None:
        if self.url_root:
            system(f"cp -r {self.assets} {self.dist}/")
        elif not path.exists(f"{self.dist}/assets"):
            system(f"ln -s ../{self.assets} {self.dist}/")


if __name__ == "__main__":
    generator = Generator(
        "pages", "generated", "templates", "assets"
    )

    generator.link_assets()
    generator.render_index(4)
