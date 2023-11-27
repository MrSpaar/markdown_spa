from webbrowser import open_new_tab
from configparser import ConfigParser
from http.server import HTTPServer, SimpleHTTPRequestHandler


class RequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        config = ConfigParser()
        config.read("config.ini")

        super().__init__(*args, directory=config["GENERATOR"]["dist_path"], **kwargs)


if __name__ == "__main__":
    server = HTTPServer(("", 8000), RequestHandler)

    try:
        open_new_tab("http://localhost:8000/")
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
