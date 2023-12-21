from .cli import main
from .generator import Generator, Extension
from .extensions import SASS, Sitemap, Tailwind

__all__ = ["Generator", "Extension", "SASS", "Sitemap", "Tailwind"]

if __name__ == "__main__":
    main()
