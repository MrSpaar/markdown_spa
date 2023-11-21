# Markdown SPA

A static website generator using:
- [`markdown`](https://pypi.org/project/Markdown/) to parse the files
- [`jinja2`](https://jinja.palletsprojects.com/en/2.10.x/) to generate the HTML
- [`livereload`](https://pypi.org/project/livereload/) for local testing (optional)

By default, Markdown-SPA includes:
- A script to avoid full page reloads
- Automatic table of contents generation
- A workflow to automatically deploy to GitHub Pages

## Usage

By default (configurable in the [`build.py`](./build.py) script):
- [`./pages`](./pages) contains the Markdown files (file based routing)
- [`./templates`](./templates) contains the Jinja2 templates
- [`./assets`](./assets) contains the static files (CSS, JS, images, etc.)
- [`./generated`](./generated) contains the generated HTML files

To build the website, install the dependencies then simply run the script:
```bash
pip install markdown jinja2
python -m build
```

> [!NOTE]
> To start a local server with live reload, run `python -m build -lr` instead (requires [`livereload`](https://pypi.org/project/livereload/)).

## Templating

The default template for the table of contents gives the following HTML and can be [customized](./templates/macros.html):
```html
<ul>
    <li><a href="/index.html"">Index</a></li>
    <li>Sub
        <ul>
            <li><a href="/sub/index.html"">Index</a></li>
        </ul>
    </li>
</ul>
```

You can modify the templates as you wish, but the following variables are available:
- `{{ url_root }}`: root URL, automatically created (repository name for GitHub Pages)
- `{{ page_content }}`: HTML content of each markdown file
- `{{ tree }}`: file tree, automatically created and used for the table of contents
- `{{ render_nav(tree) }}`: macro that renders the table of contents from the given tree
