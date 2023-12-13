order: 2
name: Styling
description: How to use CSS or SASS in your project

Pure CSS doesn't require any setup, just put your CSS files in the `assets_path` directory and link it in your HTML files:
```html
<link rel="stylesheet" href="/assets/style.css" />
```

> In the following examples, `assets_path` is set to `assets`, `templates_path` is set to `templates` and `pages_path` is set to `pages`.
> [!WARNING]

## SASS Support

You can enable SASS support by modifying the `config.ini` file:
```ini
[libsass]
enabled = true
source_path = scss
main_path = scss/main.scss
```

Then in your main SASS file you can import other SASS files:
```scss
@import "another_scss_file";
@import "some_other_scss_file";

/* Your SASS code */
```

A file named `style.css` will be generated and is automatically rebuilt when using the test server:
```html
<link rel="stylesheet" href="/assets/style.css" />
```

## Tailwind Support

To use Tailwind CSS in your project, modify the `config.ini` file:
```ini
[pytailwindcss]
enabled = true
input_file = assets/tailwind.css
config_file = tailwind.config.js
output_file = style.css
```

Then, to purge unused CSS, modify the `tailwind.config.js` file:
```js
/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["templates/**/*.html", "pages/**/*.md"],
    // ...
}
```

A CSS file will be generated and is automatically rebuilt when using the test server:
```html
<link rel="stylesheet" href="/assets/style.css" />
```