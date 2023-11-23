# Markdown SPA

A Python ([`jinja2`](https://pypi.org/project/Jinja2/) + [`markdown`](https://pypi.org/project/Markdown/)) static site generator:
- [x] No full page reloads (if JS enabled)
- [x] Customizable automatic table of contents
- [x] Fast and automatic deployment to GitHub Pages

## Usage

By default (configurable in the [`build.py`](./build.py) script):
- [`./pages`](./pages) contains the Markdown files (file based routing)
- [`./templates`](./templates) contains the Jinja2 templates
- [`./static`](./assets) contains the static files (CSS, JS, images, etc.)
- [`./generated`](./generated) contains the generated HTML files

To build the website, install the dependencies then simply run the script:
```bash
pip install markdown jinja2
python -m build
```

> [!NOTE]
> To watch for modifications and incrementaly build, run `python watch.py` instead (requires [`watchdog`](https://pypi.org/project/watchdog/)).

## Templating

You can modify the default template as much as you want, but keep in mind that the JS script:
- Listens for clicks on `a` tags with the same location origin
- Fetches the corresponding HTML file
- Replaces the body of the current page with the fetched HTML

### Variables and macros

The following default variables and macros are available in the base templates:

| Snippet                  | Description                                                         |
| :----------------------- | :------------------------------------------------------------------ |
| `{{ url_root }}`         | Root URL, automatically created (repository name for GitHub Pages)  |
| `{{ page_content }}`     | HTML content of each markdown file                                  |
| `{{ tree }}`             | File tree, automatically created and used for the table of contents |
| `{{ render_nav(tree) }}` | Macro that renders the table of contents from the given tree        |

To add your own variables, you can add attributes at the top of **each** markdown file:
```md
title: This is a title
summary: This is a description

This is the actual content of the rendered page.
```

Then, in the base template, variables with the same name will be available:
```html
<div id="app">
    <h1>{{ title }}</h1>
    <details>
        <summary>{{ summary }}</summary>
        {{ page_content }}
    </details>
</div>
```

### Table of contents

You can modify the [`render_nav`](./templates/macros.html) macro to change how the table of contents is rendered:
```jinja
{% macro render_nav(tree, full_path, url_root) -%}
{% for path, item in tree.items() -%}
    {% if item is not mapping and path != "index" -%}
        <li><a href="{{ url_root }}{{ full_path }}/{{ path }}">{{ item }}</a></li>
    {%- elif item is mapping +%}
        <li><a href="{{ url_root }}{{ full_path }}/{{ path }}">{{ path.title() }}</a>
            <ul>
                {{ render_nav(item, full_path+'/'+path, url_root) }}
            </ul>
        </li>
    {% endif -%}
{% endfor -%}
{% endmacro -%}
```

Then, in the base template:
```jinja
<ul>
    <li><a href="{{ url_root }}/">Home</a></li>
    {{+ render_nav(tree, "", url_root) -}}
</ul>
```

Which will render the following HTML:
```html
<ul>
    <li><a href="/">Home</a></li>
    
    <li><a href="/sub">Sub</a>
        <ul>
            <li><a href="/sub/test">Test</a></li>
        </ul>
    </li>
</ul>
```