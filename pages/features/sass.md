order: 2
name: SASS Support
description: How to use SASS in a Markdown-SPA project

Markdown-SPA supports SASS out of the box, you just need to set the path to the main SASS file in the configuration file to enable it:
```ini
[GENERATOR]
scss_path = sass/main.scss
```

Then in your main SASS file you can import other SASS files:
```scss
@import "another_scss_file";
@import "some_other_scss_file";

...
```

A file named `style.css` will be generated in `<dist_path>/<assets_path>`:
```html
<link rel="stylesheet" href="/assets/style.css" />
```

If any SASS file is modified, the test server will automatically recompile the SASS files and reload the page in the browser.