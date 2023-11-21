from json import dumps
from os.path import isfile, exists
from os import listdir, environ, makedirs, system

from markdown import markdown
from jinja2 import Environment, FileSystemLoader, Template


pages_path = 'pages'
assets_path = 'assets'
build_path = 'generated'
templates_path = 'templates'
url_root = ""


def read_file(path: str) -> str:
    with open(path) as f:
        return f.read()

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


def build_page(template: Template, path: str, **kwargs: object) -> str:
    return template.render(
        content=markdown(read_file(path), extensions=["fenced_code"]), **kwargs
    )

def build_tree(template: Template, tree: FileTree, full_tree: FileTree, full_path: str = "") -> None:
    for path, child in tree.items():
        if isinstance(child, str):
            html = build_page(
                template, f"{pages_path}/{full_path}/{path}.md",
                url_root=url_root, full_path=full_path, tree=full_tree
            )

            write_file(f"{build_path}/{full_path}/{path}.html", html)
            continue
        
        directory = f"{build_path}/{full_path}/{path}"
        if not exists(directory):
            makedirs(directory, exist_ok=True)

        build_tree(template, child, full_tree, f"{full_path}/{path}")


if __name__ == "__main__":
    if "URL_ROOT" in environ:
        url_root = f"/{environ['URL_ROOT']}"

    if not exists(build_path):
        makedirs(build_path, exist_ok=True)

    env = Environment(loader=FileSystemLoader(templates_path))
    template = env.get_template('base.html')
    tree = get_file_tree(pages_path)

    write_file(f"{build_path}/tree.json", dumps(tree, indent=4))
    build_tree(template, tree, tree)

    if url_root:
        system(f"cp -r {assets_path} {build_path}/")
    elif not exists(f"{build_path}/{assets_path}/"):
        system(f"ln -s ../{assets_path} {build_path}/")
