order: 1
name: Sitemap
description: Automatic sitemap and robots.txt generation

`Sitemap` comes with `Markdown-SPA` by default, it allows you to generate a `sitemap.xml` and `robots.txt` files for your website.

First, add the following to your `config.ini`:
```ini
[Sitemap]
sitemap = templates/sitemap.xml
robots = templates/robots.txt
```

You can then create the `sitemap.xml` and `robots.txt` files in the `templates` directory:

- `robots.txt` :
```
User-agent: *
Sitemap: {{ url }}/sitemap.xml
Disallow:
```

- `sitemap.xml` :
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    {% for uri, page in tree.items() recursive %}
    <url>
        <loc>{{ url }}/{{ uri }}</loc>
        <lastmod>{{ date }}</lastmod>
        <priority>{{ page.meta.priority }}</priority>
    </url>

    {% if page.children %}
        {{ loop(page.children.items()) }}
    {% endif %}
    {% endfor %}
</urlset>
```

These are the default templates that comes with blank projects, you can customize them as you wish.
A `sitemap.xml` and `robots.txt` will be generated at the root of your website.