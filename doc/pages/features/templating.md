[order]:       # (1)
[name]:        # (Templating)
[description]: # (How to use jinja2 templates in a markdown_spa project)

`markdown_spa` uses [jinja2](https://jinja.palletsprojects.com/en/2.11.x/) as a templating engine. This allows you to create a base template that will be used for all pages, and to add custom variables to each page:

| Default variable         | Description                                                         |
| ------------------------ | ------------------------------------------------------------------- |
| `{{ tree }}`             | Mapping of the directory structure                                  |
| `{{ meta }}`             | Mapping of the page's attributes                                    |
| `{{ assets_path }}`      | Path to the assets directory                                        |
| `{{ page_content }}`     | HTML content of each markdown file                                  |

To add your own variables, you can add attributes at the top of **each** file:
```markdown
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

> Pages can be HTML files in which case they will be rendered as a standalone template.
> [!NOTE]
