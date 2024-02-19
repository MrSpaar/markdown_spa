[order]:       # (1)
[name]:        # (Templating)
[description]: # (How to use jinja2 templates in a markdown_spa project)

`markdown_spa` uses [jinja2](https://jinja.palletsprojects.com/en/3.0.x/), allowing you to create a base template that will be used for all pages.
By default, the following variables are available:

| Variable                 | Available in                       | Description                        |
| :----------------------- | :--------------------------------- | :--------------------------------- |
| `{{ uri }}`              | Base and nav templates, HTML pages | URI of the page                    |
| `{{ meta }}`             | Base and nav templates, HTML pages | Mapping of the page's attributes   |
| `{{ assets_path }}`      | Base and nav templates, HTML pages | Path to the assets directory       |
| `{{ page_content }}`     | Base template                      | HTML content of each markdown file |

> [!WARNING]
> Pages can be HTML or Markdown files, but the variables are only available in HTML files.

To add your own variables, you can add attributes at the top of **each** file:
```md
[title]:   # (This is a title)
[summary]: # (This is a description)

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

Which will render as:
```html
<div id="app">
    <h1>This is a title</h1>
    <details>
        <summary>This is a description</summary>
        <p>This is the actual content of the rendered page.</p>
    </details>
</div>
```
