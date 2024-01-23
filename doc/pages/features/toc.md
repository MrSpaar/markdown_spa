[order]:       # (5)
[name]:        # (Table of Contents)
[description]: # (Automatically generated table of contents)

The table of contents at the side of this page was automatically generated from the `nav_template` in the `config.ini` file.
In blank projects, the template is the following:
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
