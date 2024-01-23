[order]:       # (4)
[name]:        # (Attributes)
[description]: # (How to add attributes to Markdown elements)

`markdown_spa` uses the [attr-list](https://python-markdown.github.io/extensions/attr_list/) to add HTML to Markdown elements:
```md
# This is a title
{: .anchored-title }

![This is an image](./image.png){: class="img center" loading="lazy" }
```

There are three types of attributes:

- HTML id: `{: #id }`
- HTML class: `{: .class }`
- Key/Value pairs: `{: loading="lazy" }`

You can add attributes to a whole block or to a single element:
```md
This is a block that will have the text-center class
because the attribute list is on the last line of the block
{: .text-center }

![Image with an inline attribute list](./image.png){: class="img center" loading="lazy" }
```