order: 3
name: Tailwind
description: How to use Tailwind CSS in your project

To use Tailwind CSS in your project, modify the `config.ini` file:
```ini
[Tailwind]
input_file = assets/tailwind.css
config_file = tailwind.config.js
```

Then, to purge unused CSS, modify the `tailwind.config.js` file:
```js
/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["templates/**/*.html", "pages/**/*.md"],
    // ...
}
```

And at the beggining of your input file:
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
