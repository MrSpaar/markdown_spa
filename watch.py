from build import Generator
from livereload import Server


if __name__ == "__main__":
    generator = Generator("config.ini")
    generator.build()

    server = Server()
    server.watch(f"{generator.pages_path}/", generator.build)
    server.watch(f"{generator.templates_path}/", generator.build)

    if generator.config["SASS"].getboolean("enabled"):
        server.watch(f"{generator.config['SASS']['source_path']}/", generator.build_sass)

    server.serve(root=generator.dist_path, port=generator.port, open_url_delay=0)
