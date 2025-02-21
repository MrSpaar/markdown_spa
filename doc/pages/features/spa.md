[order]:       # (3)
[name]:        # (Single Page App)
[description]: # (Control how pages are loaded)

Any project comes with `markdown_spa.js` in the assets folder. This simple script controls how pages are loaded and what content is updated.
Whenever a link to another page is clicked or a popstate event is fired, the script will:

- Call the `preFetch()` function if it exists
- Fetch the page and update the content
- Call the `postFetch()` function if it exists

> [!TIP]
> You can override the `preFetch()` and `postFetch()` functions to add custom logic.

By default the new page if fetched and replaces the entire document. However, if you want to modify specific parts of the page, you can use the JSON mode:

- Enable JSON in the `config.ini` file:
```ini
[GENERATOR]
json = true
```
- A JSON file will be generated for each page
```json
{
    "uri": "/uri/to/page",
    "page_content": "...",
    "any_meta_tag": "..."
}
```
- Add a `updateWithJSON` function to your website:
```js
function updateWithJSON(json) {
    // Update the page with the JSON data, for instance:
    document.getElementById("content").innerHTML = json.page_content;

    // If we have a title meta tag, we can update the page title
    document.title = json.title;
}
```
