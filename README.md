# Markdown-SPA

A Python ([`jinja2`](https://pypi.org/project/Jinja2/) + [`markdown`](https://pypi.org/project/Markdown/)) static site generator:

- [x] No full page reloads (if JS enabled)
- [x] Customizable automatic table of contents
- [x] Fast and automatic deployment to GitHub Pages

## Usage

To build your website :

- Install the dependencies: `pip install markdown jinja2 Pygments libsass`
- Configure the [`config.ini`](https://github.com/MrSpaar/Markdown-SPA/blob/master/config.ini) file (if needed)
- Run `python -m build`

> [!NOTE]
> To start a test server and file watcher, run `python watch.py` (requires [`watchdog`](https://pypi.org/project/watchdog/))

## SASS support

To use SASS, simply create a `main.scss` file in the configured `<scss_path>` directory:
```scss
@import "some_other_scss_file";
@import "another_scss_file";

...
```

A file named `style.css` will be generated in `<dist_path>/<assets_path>` directory:
```html
<!-- Root is 'dist_path', so if 'assets_path' is set to 'assets', the href is '/assets/style.css' -->
<link rel="stylesheet" href="/assets/style.css" />
```

> [!NOTE]
> The file watcher will automatically recompile SASS files only if `<scss_path>` is set.

## Markdown attributes

Markdown-SPA uses the [`attr-list`](https://python-markdown.github.io/extensions/attr_list/) extension to add kramdown-like attributes to Markdown elements:
```md
# This is a title
{: .anchored-title }

![This is an image](./image.png){: class="img center" loading="lazy" }
```

## Syntax highlighting

Syntax highlighting in code blocks is done using the [`codehilite`](https://python-markdown.github.io/extensions/code_hilite/) and [`fenced_code`](https://python-markdown.github.io/extensions/fenced_code_blocks/) extensions. Multiple code block syntaxes are supported::
````
```python
print("Hello World!")
```

    :::python
    print("Hello World!")

    #!python
    print("Hello World!")
````

Specifying the language is optional and [`Pygments`](https://pygments.org/) is used to highlight the code.

## Template variables and macros

The following default variables and macros are available in the base templates:

| Snippet                  | Description                                                         |
| ------------------------ | ------------------------------------------------------------------- |
| `{{ tree }}`             | Mapping of the markdown files directory structure                   |
| `{{ meta }}`             | Mapping of the markdown file attributes                             |
| `{{ assets_path }}`      | Path to the assets directory                                        |
| `{{ page_content }}`     | HTML content of each markdown file                                  |

To add your own variables, you can add attributes at the top of **each** markdown file:
```md
title: This is a title
summary: This is a description

This is the actual content of the rendered page.
```

Then, in the base template, variables with the same name will be available:
```html
<div id="app">
    <h1>{{ meta.title }}</h1>
    <details>
        <summary>{{ meta.summary }}</summary>
        {{ page_content }}
    </details>
</div>
```

## Table of contents

You can modify the [`nav.html`](https://github.com/MrSpaar/Markdown-SPA/blob/master/templates/nav.html) template to change how the table of contents is rendered:
```jinja
{% macro render_nav(tree, root) %}
<ul>
    {% if root %}
        <li><a href="/{{ tree.path }}">{{ tree.meta.name }}</a></li>
    {% endif %}

    {%- for child in tree.children %}
        {% if child.children %}
            <li><a href="/{{ child.path }}">{{ child.meta.name }}</a>
                {{ render_nav(child, False) }}
            </li>
        {% else %}
            <li><a href="/{{ child.path }}">{{ child.meta.name }}</a></li>
        {% endif %}
    {% endfor %}
</ul>
{% endmacro %}

{{ render_nav(tree, True) }}
```

Which will render the following HTML:
```html
<ul>
    <li><a href="/">Main page</a></li>
    <li><a href="/sub">Sub category</a>
        <ul>
            <li><a href="/sub/test">Test page</a></li>
        </ul>
    </li>
</ul>
```