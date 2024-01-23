from os import environ

from .cli import main
from .generator import Generator, Extension
from .extensions import SASS, Sitemap, Tailwind


__all__ = ["Generator", "Extension", "SASS", "Sitemap", "Tailwind"]
__version__ = environ.get("MARKDOWN_SPA_VERSION", "0.0.0").removeprefix("v")


if __name__ == "__main__":
    main()
