from os import environ
from requests import get

from .cli import main
from .generator import Generator, Extension
from .extensions import SASS, Sitemap, Tailwind


__all__ = ["Generator", "Extension", "SASS", "Sitemap", "Tailwind"]
__version__ = environ.get(
    "MARKDOWN_SPA_VERSION",
    get("https://pypi.org/pypi/markdown_spa/json").json()["info"]["version"]
).removeprefix("v")


if __name__ == "__main__":
    main()
