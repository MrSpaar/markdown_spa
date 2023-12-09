order: 2
name: Styling
description: How to use CSS or SASS in your project

Pure CSS doesn't require any setup, just put your CSS files in the `assets_path` directory and link it in your HTML files:
```html
<link rel="stylesheet" href="/assets/style.css" />
```

## SASS Support

If you didn't enable it during the project creation, you can modify the `config.ini` file to enable SASS support:
```ini
[SASS]
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

A file named `style.css` will be generated in `dist_path/assets_path`:
```html
<link rel="stylesheet" href="/assets/style.css" />
```

If any SASS file is modified, the test server will automatically recompile the SASS files and reload the browser.
