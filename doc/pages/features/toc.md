order: 5
name: Table of Contents
description: Automatically generated table of contents

The table of contents at the side of the page was automatically generated from the [`nav.html`](https://github.com/MrSpaar/Markdown-SPA/blob/master/templates/nav.html) template:
```jinja
<ul>
    {% for (uri, page) in tree.items() recursive -%}
    <li><a href="/{{ uri }}">{{ page.meta.name }}</a>
        {% if page.children -%}
        <ul>
            {{ loop(page.children.items()) }}
        </ul>
        {% endif -%}
    </li>
    {% endfor -%}
</ul>
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
