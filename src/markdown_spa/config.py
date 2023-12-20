from os.path import exists
from os import environ, devnull
from importlib import import_module
from subprocess import call, STDOUT 
from configparser import ConfigParser

def silent_call(command: str) -> int:
    return call(command, shell=True, stdout=open(devnull, "w"), stderr=STDOUT)

def ensure_lib(module: str, package: str = "") -> bool:
    try:
        import_module(module)
        return True
    except ModuleNotFoundError:
        return silent_call(f"pip install {package or module}") == 0

class IniConfig(ConfigParser):
    def __init__(self, root: str, ini_file: str = "config.ini") -> None:
        super().__init__()

        if not exists(f"{root}/{ini_file}"):
            raise Exception(f"Missing '{ini_file}' config file")
        
        self.read(f"{root}/{ini_file}")
        if not self.has_section("GENERATOR"):
            raise Exception("No 'GENERATOR' section in config.ini")
        
        if not self.has_option("GENERATOR", "port"):
            raise Exception("Missing 'port' parameter in 'GENERATOR' section")

        if not self.has_option("GENERATOR", "dist_path"):
            raise Exception("Missing 'dist_path' parameter in 'GENERATOR' section")

        self.dist_path: str = ""
        self.pages_path: str = ""
        self.assets_path: str = ""
        self.templates_path: str = ""
        
        for param in ("pages_path", "assets_path", "templates_path"):
            if not self.get("GENERATOR", param):
                raise Exception(f"Missing '{param}' parameter in 'GENERATOR' section")
        
            path = f"{root}/{self.get('GENERATOR', param)}"
            setattr(self, param, path)
            
            if not exists(path):
                raise Exception(f"Parameter '{param}': path '{path}' does not exist")

        for template in ("base.html", "nav.html"):
            if not exists(f"{self.templates_path}/{template}"):
                raise Exception(f"Missing '{template}' template")

        self.root = root
        self.port = self.getint("GENERATOR", "port")
        self.base_url = f"http://localhost:{self.port}"

        if var := environ.get("REPO"):
            user, repo = var.split("/")
            self.base_url = f"https://{user}.github.io/{repo}"
        
        self.dist_path = f"{root}/{self.get('GENERATOR', 'dist_path')}"
        self.dist_assets_path = f"{self.dist_path}/{self.assets_path[self.assets_path.find('/')+1:]}"

    def check_options(self, section: str, *options: tuple[str, bool]) -> None:
        errors = "Errors in config.ini:"

        for option, should_exist in options:
            if not self.has_option(section, option):
                errors +=  f"\n  - Missing '{option}' option"
                continue
            
            path = f"{self.root}/{self.get(section, option)}"
            if should_exist and not exists(path):
                errors += f"\n  - Path '{path}' is invalid"
        
        if len(errors) > 21:
            raise Exception(errors)
