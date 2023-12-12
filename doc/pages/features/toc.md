order: 5
name: Table of Contents
description: Automatically generated table of contents

The table of contents at the side of the page was automatically generated from the [`nav.html`](https://github.com/MrSpaar/Markdown-SPA/blob/master/templates/nav.html) template:
```jinja
{% macro render_nav(tree, root) -%}
<ul>
{% for uri, page in tree.items() | sort(attribute='1.meta.order') -%}
    {% if page.children -%}
    <li><a href="/{{ uri }}">{{ page.meta.name }}</a>
        {{ render_nav(page.children, False) }}
    </li>
    {% else -%}
    <li><a href="/{{ uri }}">{{ page.meta.name }}</a></li>
    {% endif -%}
{% endfor -%}
</ul>
{% endmacro -%}

{{ render_nav(tree) }}

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

You can modify the template as long as the name of the file is `nav.html` and it is located in the `templates` directory.
