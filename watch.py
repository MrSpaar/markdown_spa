from build import Generator
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, DirModifiedEvent

from webbrowser import open_new_tab
from configparser import ConfigParser
from http.server import HTTPServer, SimpleHTTPRequestHandler


class ScssHandler(FileSystemEventHandler):
    def __init__(self, generator: Generator) -> None:
        self.file_modified = False
        self.generator = generator

    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent):
        if isinstance(event, DirModifiedEvent) or self.file_modified:
            self.file_modified = False
            return

        self.file_modified = True
        try:
            self.generator.build_css()
        except Exception as e:
            print(f"Build failed! ({e})")

class HtmlHandler(FileSystemEventHandler):
    def __init__(self, generator: Generator) -> None:
        self.file_modified = False
        self.generator = generator

    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent):
        if isinstance(event, DirModifiedEvent) or self.file_modified:
            self.file_modified = False
            return
        
        self.file_modified = True
        try:
            self.generator.build()
        except Exception as e:
            print(f"Build failed! ({e})")


class RequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        config = ConfigParser()
        config.read("config.ini")

        super().__init__(*args, directory=config["GENERATOR"]["dist_path"], **kwargs)


if __name__ == "__main__":
    generator = Generator("config.ini")
    generator.build()

    server = HTTPServer(("", 8000), RequestHandler)
    handler = HtmlHandler(generator)

    observer = Observer()

    if generator.scss_path:
        observer.schedule(
            ScssHandler(generator),
            generator.scss_path[:generator.scss_path.index('/')]
        )

    observer.schedule(handler, generator.templates_path)
    observer.schedule(handler, generator.pages_path, recursive=True)

    try:
        open_new_tab("http://localhost:8000/")
        observer.start()
        server.serve_forever()
    except KeyboardInterrupt:
        observer.stop()
        server.server_close()
