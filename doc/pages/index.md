[order]:       # (1)
[priority]:    # (1)
[name]:        # (Quick Start)
[description]: # (A Python static site generator using Markdown, Jinja2, Pygments and libsass)

[`markdown_spa`](https://github.com/MrSpaar/markdown_spa) is a Python ([jinja2](https://pypi.org/project/Jinja2/) + [markdown](https://pypi.org/project/Markdown/)) static site generator:

- [x] Powerful templating
- [x] SEO optimized
- [x] No full page reloads
- [x] SCSS and Tailwind CSS support
- [x] Extented Markdown syntax
- [x] Automatic deployment to GitHub Pages

First, to setup a new project:

- Install the package (once): `pip install markdown_spa`
- Create a blank project: `markdown_spa init <folder (optionnal)>`

The `config.ini` file describes the project structure:

| Key              | Default value | Description                               |
| :--------------- | :-----------: | :---------------------------------------- |
| `port`           | `8000`        | Port used by the live-reload server       |
| `pages_path`     | `pages`       | Root of all markdown files                |
| `assets_path`    | `assets`      | Root of all assets (images, css, js, ...) |
| `scss_path`      | `scss`        | Root of all SCSS files (optionnal)        |
| `dist_path`      | `dist`        | Root of the generated website             |
| `templates_path` | `templates`   | Root of all templates                     |

And finally, to build your website you have two options:

- Standalone: `markdown_spa build <folder (optionnal)>`
- Live-reload: `markdown_spa watch <folder (optionnal)>`

> [!NOTE]
> If scripts aren't added to `PATH`, you can use `python -m markdown_spa` instead of `markdown_spa`.