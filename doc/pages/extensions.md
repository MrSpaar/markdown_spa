order: 4
name: Extensions
description: Documentation on Markdown-SPA's extension system

Markdown-SPA has a simple extension system that allows you to add custom functionality to your site.
To install an extension, simply run the following command:
```bash
markdown_spa install <extension-name> <git_repo_url>
```

This will install the extension globally for your user.
Markdown-SPA will automatically load all extensions in the `config.ini` file:
```ini
[extension-name]
extension_option = value
...
```

## Create an extension

You can then use the `Extension` class to create an extension:
```python
from markdown_spa.extension import Extension, Generator

class MyExtension(Extension):
    def __init__(self, generator: Generator) -> None:
        super().__init__(generator)
        ...
    
    @staticmethod
    def initialize() -> None:
        # Called when the extension is added to a project
        # either via `markdown_spa init` or `markdown_spa add`
    
    def render(self) -> None:
        # Called when the site is generated
        # either via `markdown_spa build` or `markdown_spa watch`
```

The `__init__` function can be used to:

- Validate the user's configuration
```python
self.config.check_options(
    self.name,              # Name of the extension, always self.name     
    ("option1", True),      # True = will check if the value is a valid path
    ("option2", False)      # False = no path validation
)
```
- Set which files or directories the extension should watch for changes
```python
self.to_watch = [
    "path/to/file",
    "path/to/directory"
]
```

## Make an extension available to the user

Every Markdown-SPA extension must be a Python module that contains a class that inherits from `markdown_spa.Extension`.
The class' name determines the name of the extension and is used to install it.

Here is a minimal example of an extension:

- File structure:
```
myRepo
  ├── .git
  └── __init__.py
```
- `__init__.py`:
```python
from markdown_spa import Extension, Generator


class MyExtension(Extension):
    ...
```
- User can then install the extension with :
```bash
markdown_spa install MyExtension <git_repo_url>
```