from build import build
from livereload import Server


if __name__ == '__main__':
    server = Server()

    server.watch('assets/*', build)    
    server.watch('pages/*', build)
    server.watch('templates/*', build)

    server.serve(
        port=5000,
        liveport=5050,
        root="generated"
    )
