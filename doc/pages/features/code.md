order: 3
name: Syntax Highlighting
description: Syntax highlighting in code blocks

Syntax highlighting in code blocks is done using the [codehilite](https://python-markdown.github.io/extensions/code_hilite/) and [fenced_code](https://python-markdown.github.io/extensions/fenced_code_blocks/) extensions. You can create code blocks (language name can be deduced):

- With a shebang (to show line numbers)
```markdown
    #!python
    print("Hello World!")
```
- With three backticks (uses [attr_list](https://python-markdown.github.io/extensions/attr_list/))
````markdown
```python
print("Hello World!")
```
````

If you want to highlight lines, you can use the `hl_lines` option:

- With three backticks (uses [attr_list](https://python-markdown.github.io/extensions/attr_list/))
````markdown
``` { .python hl_lines="1 3" }
print("Hello", end=" ")
print("World", end="")
print("!")
```
````
- With a shebang (to show line numbers)
```
    #!python hl_lines="1 3"
    print("Hello", end=" ")
    print("World", end="")
    print("!")
```

This will render as:

    #!python hl_lines="1 3"
    print("Hello", end=" ")
    print("World", end="")
    print("!")