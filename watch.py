from build import *
from os import chdir
from webbrowser import open_new_tab
from http.server import HTTPServer, SimpleHTTPRequestHandler

from watchdog.events import *
from watchdog.observers import Observer


env = Environment(loader=FileSystemLoader(templates_path))
template = env.get_template('base.html')

tree = get_file_tree(pages_path)
md = Markdown(extensions=[
    "meta", "tables", "attr_list", "fenced_code",
    CodeHiliteExtension(css_class="highlight")
])


class Handler(FileSystemEventHandler):
    def __init__(self):
        self.run_once = False
    
    def check_run(self):
        self.run_once = not self.run_once
        return self.run_once
    
    def rebuild_tree(self, template_modifed: bool = False):
        global template

        if self.check_run():
            return

        if template_modifed:
            template = env.get_template('base.html')

        build_tree(template, md, tree, tree)
        print("Rebuilt entire site")


class TemplateHandler(Handler):
    def on_modified(self, event: FileModifiedEvent | DirModifiedEvent):
        if isinstance(event, FileModifiedEvent):
            self.rebuild_tree()

class PagesHandler(Handler):
    def __init__(self):
        super().__init__()
        self.file_modified = False
        self.on_moved = self.rebuild_tree
        self.on_deleted = self.rebuild_tree
    
    def on_modified(self, event: FileModifiedEvent | DirModifiedEvent):
        if self.check_run():
            return

        if isinstance(event, DirModifiedEvent) and self.file_modified:
            self.file_modified = False
            return
        
        if isinstance(event, DirModifiedEvent):
            return self.rebuild_tree()
        
        self.file_modified = True
        full_path = event.src_path[len(pages_path) + 1:event.src_path.rfind("/")]

        html = build_page(
            template, md, event.src_path,
            url_root=url_root, full_path=full_path, tree=tree, assets_path=assets_path
        )

        if 'index.md' in event.src_path:
            dist = f"{full_path}/index.html".removeprefix("/")
        else:
            dist = f"{event.src_path[len(pages_path) + 1:-3]}/index.html"

        write_file(f"{build_path}/{dist}", html)
        print(f"Rebuilt {dist}")


class RequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=build_path, **kwargs)


if __name__ == "__main__":
    observer = Observer()
    server = HTTPServer(("", 8000), RequestHandler)

    observer.schedule(TemplateHandler(), path=f"{templates_path}")
    observer.schedule(PagesHandler(), path=f"{pages_path}", recursive=True)

    try:
        open_new_tab("http://localhost:8000/")
        observer.start()
        server.serve_forever()
    except KeyboardInterrupt:
        observer.stop()
        server.server_close()
