[order]:       # (3)
[name]:        # (JSON files)
[description]: # (Generate JSON files for finer control over page updates)

To get finer control over page updates, you can generate a JSON file along with each page.
Every json file will contain the following information:

- `uri`: The URI of the page
- `page_content`: The rendered HTML of the page
- All meta tags defined in the page

For instance, with the following page (`pages/my-page.md`):
```md
[order]:       # (1)
[name]:        # (My page)
[description]: # (This is my page)

# My page
```

The following JSON file will be generated:
```json
{
    "uri": "/my-page",
    "page_content": "<h1>My page</h1>",
    "order": "1",
    "name": "My page",
    "description": "This is my page"
}
```

Then in the default `script.js` file, you can modify the `update` function to do whatever you want with the JSON files:
```js
function update(path, push = true) {
    fetch(path + 'index.json')
        .then(resp => resp.json())
        .then(json => {
            document.title = json.name;
            document.querySelector('meta[name="description"]').content = json.description;
            // ...

            if (push)
                window.history.pushState({}, '', path);

            prepare();
        });
}
```
