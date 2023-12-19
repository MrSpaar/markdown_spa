from os import devnull
from subprocess import call, STDOUT


def silent_call(command: str) -> int:
    return call(command, shell=True, stdout=open(devnull, "w"), stderr=STDOUT)


def enable(import_name: str, package: str, ini: str = "") -> int:
    try:
        __import__(import_name)
    except ImportError:
        return silent_call(f"pip install {package}")

    return 0
