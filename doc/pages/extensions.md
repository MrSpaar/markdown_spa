order: 4
name: Extensions
description: Documentation on Markdown-SPA's extension system

Markdown-SPA has a simple extension system that allows you to add custom functionality to your site.

## Install an extension

To install an extension, simply run `markdown_spa install <extension-name> <git_repo_url>`.
This will install the extension globally for your user (in `site-packages/markdown_spa/extensions`).

To then use this extension in a project, add a section to your `config.ini` file:
```ini
[extension-name]
; Any configuration options for the extension
```

Markdown-SPA will automatically load all extensions in the `config.ini` file.

## Create an extension

To create an extension, the root of your git repository must contain:

- A `__init__.py` that imports your extension class
- A `requirements.txt` that contains all dependencies for your extension

You can then use the `Extension` class to create an extension:
```python
from markdown_spa.extension import Extension, Generator


class MyExtension(Extension):
    def __init__(self, generator: Generator) -> None:
        super().__init__(generator)
        # Do any setup here
    
    @staticmethod
    def initialize() -> None:
        # Executed during blank project creation
        # or when 'markdown_spa add MyExtension' is run
    
    def render(self) -> None:
        # Main logic of the extension
```

If you want to validate the user's configuration, you can use the `check_options` method:
```python
self.config.check_options(
    self.name,           # Name of the extension, always self.name     
    (
        "option1",       # Name of the option
        True             # True = will check if the value is a valid path
    ),
    (
        "option2",       # Name of the option
        False            # False = no path validation
    )
)
```

If you need your extension to render when specific files or directories are changed, you can override the `to_watch` variable:
```python
# In __init__
self.to_watch = [
    "path/to/file",
    "path/to/directory"
]
```
