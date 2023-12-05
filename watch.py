from build import Generator
from livereload import Server


if __name__ == "__main__":
    generator = Generator("config.ini")
    generator.link_assets()
    generator.build()

    server = Server()

    server.watch(f"{generator.pages_path}/", generator.build)
    server.watch(f"{generator.templates_path}/", generator.build)
    server.watch(f"{generator.scss_path[:generator.scss_path.rfind('/')]}/", generator.build_css)

    server.serve(root=generator.dist_path, port=8080, open_url_delay=0)
