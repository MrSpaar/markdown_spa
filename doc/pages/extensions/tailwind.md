[order]:       # (3)
[name]:        # (Tailwind)
[description]: # (How to use Tailwind CSS in your project)

The Tailwind extension allows you to use Tailwind CSS in your templates and markdown files.

To add it to an existing project, run `markdown_spa add Tailwind`, there are two options:

- `config_file`: The path to the Tailwind config file (relative to project root)
- `input_file`: The path to the input CSS file (optional, relative to project root)

> [!WARNING]
> The automatic configuration will delete `assets/style.css` if it exists.

## Manual configuration

First, modify your `config.ini` file to add the following section:
```ini
[Tailwind]
input_file = assets/tailwind.css
config_file = tailwind.config.js
```

Then, to purge unused CSS, create a `tailwind.config.js` file:
```js
/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["templates/**/*.html", "pages/**/*.md"],
    // ...
}
```

You can now use tailwind in your templates and markdown files.
Optionally, you can have an input CSS file, it just needs the following content:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Your CSS code */
```

A file named `style.css` will be generated and is automatically rebuilt when using the test server:
```html
<link rel="stylesheet" href="/assets/style.css" />
```
