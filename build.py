from json import dump
from string import Template
from markdown import markdown
from os import listdir, path, makedirs, environ

NestedDict = dict[str, "str | NestedDict"]


class Rendered:
    def __init__(self, src: str, dist: str, templates: str) -> None:
        self.url_root = ""
        if 'URL_ROOT' in environ:
            self.url_root = "/"+environ['URL_ROOT'].split('/')[1]

        if not path.exists(dist):
            makedirs(dist, exist_ok=True)

        self.dist = dist
        self.structure: NestedDict = self.render_pages(src, dist)

        with open("./generated/structure.json", "w") as f:
            dump(self.structure, f, indent=4)

        self.templates: dict[str, Template] = {}
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

    def render_nav(self, indents: int) -> str:
        return self._render_nav(self.structure, self.url_root + self.dist[1:], indents, True)

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


if __name__ == "__main__":
    renderer = Rendered("pages/", "./generated/pages/", "templates/")

    with open("./generated/index.html", "w") as f:
        f.write(renderer.render_template(
            "index.html", url_root=renderer.url_root, nav=renderer.render_nav(8)
        ))
    