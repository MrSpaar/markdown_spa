priority: 1
name: Quick start
description: A Python static site generator using Markdown, Jinja2, Pygments and libsass

[Markdown-SPA](https://github.com/MrSpaar/Markdown-SPA) is a Python ([`jinja2`](https://pypi.org/project/Jinja2/) + [`markdown`](https://pypi.org/project/Markdown/)) static site generator:

- [x] Powerful templating
- [x] SEO optimized
- [x] No full page reloads
- [x] SCSS support ([`libsass`](https://pypi.org/project/libsass/))
- [x] Extented Markdown syntax
- [x] Automatic deployment to GitHub Pages

<br>

First, to setup a new project:
```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/MrSpaar/Markdown-SPA/master/setup.sh)"
```

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
```bash
# Build the website once
python -m build

# Start a live-reload server (requires `livereload`)
python watch.py
```
