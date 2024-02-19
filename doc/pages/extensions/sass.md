[order]:       # (2)
[name]:        # (SASS)
[description]: # (How to use SASS in your project)

The SASS extension allows you to use SASS in your project.

To add it to an existing project, run `markdown_spa add SASS`, there are two options:

- `source_path`: The path to the directory containing your SASS files
- `main_path`: The path to the main SASS file (relative to project root)

> [!WARNING]
> The automatic configuration will delete `assets/style.css` if it exists.

## Manual configuration

First, modify your `config.ini` file to add the following section:
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
