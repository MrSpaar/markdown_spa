from ..extension import Extension

from shutil import copy
from datetime import datetime
from typing import TYPE_CHECKING

from click import prompt
from jinja2 import Template

if TYPE_CHECKING:
    from ...generator import Generator


class Sitemap(Extension):
    def __init__(self, generator: 'Generator') -> None:
        super().__init__(generator)
        
        self.config.check_options(self.name, ("sitemap", True), ("robots", True))
        self.to_watch = [
            f"{self.config.root}/{self.config.get(self.name, 'robots')}",
            f"{self.config.root}/{self.config.get(self.name, 'sitemap')}"
        ]

        with open(self.to_watch[0]) as f:
            self.robots_template = Template(f.read())

        with open(self.to_watch[1]) as f:
            self.sitemap_template = Template(f.read())

    @staticmethod
    def initialize() -> None:
        robots = prompt(
            "Enter the path to the robots template (default: ./templates/robots.txt)",
            default="templates/robots.txt", prompt_suffix=": ", show_default=False
        )

        sitemap = prompt(
            "Enter the path to the sitemap template (default: ./templates/sitemap.xml)",
            default="templates/sitemap.xml", prompt_suffix=": ", show_default=False
        )

        copy(f"{Sitemap.path}/robots.txt", robots)
        copy(f"{Sitemap.path}/sitemap.xml", sitemap)

        with open("config.ini", "a") as file:
            file.write(f"\n[Sitemap]\nrobots = {robots}\nsitemap = {sitemap}\n")


    def render(self) -> None:
        with open(f"{self.config.dist_path}/robots.txt", "w") as f:
            f.write(self.robots_template.render(url=self.config.base_url))

        with open(f"{self.config.dist_path}/sitemap.xml", "w") as f:
            f.write(self.sitemap_template.render(
                tree=self.generator.tree, url=self.config.base_url,
                date=datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")
            ))
