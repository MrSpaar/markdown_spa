from sys import argv
from os.path import isfile, exists
from os import listdir, environ, makedirs, system

from markdown import Markdown
from markdown.extensions.meta import MetaExtension
from markdown.extensions.attr_list import AttrListExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.codehilite import CodeHiliteExtension
from jinja2 import Environment, FileSystemLoader, Template


pages_path = 'pages'
assets_path = 'static'
build_path = 'generated'
templates_path = 'templates'

in_github_actions = "URL_ROOT" in environ
url_root = f"/{environ['URL_ROOT'].split('/')[1]}" \
                if in_github_actions else ""


def write_file(path: str, content: str) -> None:
    with open(path, 'w') as f:
        f.write(content)

FileTree = dict[str, "str | FileTree"]
def get_file_tree(parent: str = "") -> FileTree:
    tree: FileTree = {}

    for path in listdir(parent):
        child = parent + "/" + path

        if isfile(child):
            name = path[:-3]
            tree[name] = name.title()
        else:
            tree[path] = get_file_tree(child)

    return tree


def build_page(template: Template, md: Markdown, path: str, **kwargs: object) -> str:
    with open(path) as f:
        content = f.read()
    
    html = Template(md.convert(content)).render(**kwargs)
    return template.render(page_content=str(html), **md.Meta, **kwargs)

def build_tree(template: Template, md: Markdown, tree: FileTree, full_tree: FileTree, full_path: str = "") -> None:
    for path, child in tree.items():
        if isinstance(child, dict):
            directory = f"{build_path}/{full_path}/{path}"
            if not exists(directory):
                makedirs(directory, exist_ok=True)

            build_tree(template, md, child, full_tree, f"{full_path}/{path}")
            continue
        
        html = build_page(
            template, md, f"{pages_path}/{full_path}/{path}.md",
            url_root=url_root, full_path=full_path, tree=full_tree, assets_path=assets_path
        )

        if path == "index":
            write_file(f"{build_path}/{full_path}/index.html", html)
        else:
            makedirs(f"{build_path}/{full_path}/{path}", exist_ok=True)
            write_file(f"{build_path}/{full_path}/{path}/index.html", html)


if __name__ == "__main__":
    if not exists(build_path):
        makedirs(build_path, exist_ok=True)

    env = Environment(loader=FileSystemLoader(templates_path))
    template = env.get_template('base.html')

    tree = get_file_tree(pages_path)
    md = Markdown(extensions=[
        MetaExtension(),
        AttrListExtension(),
        FencedCodeExtension(),
        CodeHiliteExtension(css_class="highlight"),
    ])

    build_tree(template, md, tree, tree)
    if not exists(f"{build_path}/{assets_path}"):
        system(f"cp -r {assets_path} {build_path}/" if in_github_actions
               else f"ln -s ../{assets_path} {build_path}/")

    print("Build complete!")
