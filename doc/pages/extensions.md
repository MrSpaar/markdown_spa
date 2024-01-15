[order]:       # (4)
[name]:        # (Extensions)
[description]: # (Documentation on markdown_spa's extension system)

`markdown_spa` has a simple extension system that allows you to add custom functionality to your site.
To install an extension, simply run the following command:
```bash
markdown_spa install <extension-name> <git_repo_url>
```

This will install the extension globally for your user.
`markdown_spa` will automatically load all extensions in the `config.ini` file:
```ini
[extension-name]
extension_option = value
...
```

## Create an extension

`markdown_spa` has an `Extension` abstract class that you can use:
```python
from markdown_spa.extension import Extension, Dependency, Option

class MyExtension(Extension):
    DEPENDENCIES = (
        Dependency("import_name", "pip_package_name"),
        ...
    )
    OPTIONS = {
        "option_name": Option(default="default_value")
        # if is_path=True, os.path.exists will be called on the value
        # if is_template=True, the template path will be prepended to the checked path
    }
    
    @property
    def TO_WATCH(self) -> List[str]:
        # Any changes to these files will trigger a MyExtension.render
        return [
            "path/to/file",                                   # Regular file
            f"{self.root}/{self.get_option('option_name')}"   # Value of an option
        ]

    def render(self) -> None:
        # Called either via `markdown_spa build`
        # or `markdown_spa watch` (if TO_WATCH is not empty)

    @staticmethod
    def initialize() -> None:
        # Called when the extension is added to a project
        # either via `markdown_spa init` or `markdown_spa add`
```

Dependencies will be automatically installed and that part of the initialization process is automated:

- Option values are prompted to the user
- The `config.ini` file is updated with the user's input

## Make an extension available to the user

Every `markdown_spa` extension must be a Python module that contains a class that inherits from `markdown_spa.Extension` 
(class name = extension name).

Here is a minimal example of an extension:

- File structure:
```
myRepo
  ├── .git
  └── __init__.py
```
- `__init__.py`:
```python
from markdown_spa import Extension

class MyExtension(Extension):
    ...
```
- Users can then install the extension with :
```bash
markdown_spa install MyExtension <git_repo_url>
```