from shutil import copy
from datetime import datetime
from configparser import ConfigParser

from ...generator import Extension, Option


class Sitemap(Extension):
    OPTIONS = {
        "robots": Option(default="robots.txt", is_template=True),
        "sitemap": Option(default="sitemap.xml", is_template=True),
    }

    @property
    def TO_WATCH(self) -> list[str]:
        return [
            f"{self.config.root}/{self.get_option('robots')}",
            f"{self.config.root}/{self.get_option('sitemap')}",
        ]

    def render(self) -> None:
        robots_template = self.generator.env.get_template(
            self.get_option("robots")
        )

        sitemap_template = self.generator.env.get_template(
            self.get_option("sitemap")
        )

        with open(f"{self.config.dist_path}/robots.txt", "w") as f:
            f.write(robots_template.render(url=self.config.base_url))

        with open(f"{self.config.dist_path}/sitemap.xml", "w") as f:
            f.write(sitemap_template.render(
                tree=self.generator.tree, url=self.config.base_url,
                date=datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00")
            ))

    @staticmethod
    def initialize(**kwargs) -> None:
        config = ConfigParser()
        config.read("config.ini")

        copy(
            f"{Sitemap.PATH}/robots.txt",
            f"{config.get('TEMPLATES', 'templates_path')}/{kwargs['robots']}"
        )

        copy(
            f"{Sitemap.PATH}/sitemap.xml",
            f"{config.get('TEMPLATES', 'templates_path')}/{kwargs['sitemap']}"
        )
