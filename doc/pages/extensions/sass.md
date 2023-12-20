order: 2
name: SASS
description: How to use SASS in your project

You can enable SASS support by modifying the `config.ini` file:
```ini
[SASS]
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

> You can skip all the configuration by running `markdown_spa add SASS`, note that this will delete `assets/style.css` if it exists.
> [!NOTE]
