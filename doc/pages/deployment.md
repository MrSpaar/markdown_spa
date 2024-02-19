[order]:       # (2)
[name]:        # (Deployment)
[description]: # (How to setup automatic Github Pages deployment)

Github-SPA includes a Github Actions workflow to automatically deploy a static website to Github Pages.
To enable it, go to your repository's settings and choose `Github Actions` as source in the `Pages` section:
![Enable Github Pages](/static/gh-pages.webp){: width="681" height="469" }

Then, each relevant commit will trigger a new deployment using the `.github/static.yml` workflow (included in blank projects):
``` { .yaml hl_lines="41" }
name: Build and Deploy 🚀

on:
  push:
    branches:
      - master

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout 🔔
        uses: actions/checkout@v4
      - name: Setup Python 🐍
        uses: actions/setup-python@v4.7.1
        with:
          python-version: 3.12
      - name: Install dependencies 🧰
        run: python -m pip install markdown_spa
      - name: Generate HTML 📚
        run: python -m markdown_spa build
        env:
          REPO: ${{ github.repository }}
      - name: Setup Pages ⚙️
        uses: actions/configure-pages@v3
      - name: Upload artifact 📤
        uses: actions/upload-pages-artifact@v2
        with:
          path: './generated'
      - name: Deploy to GitHub Pages 🌍
        id: deployment
        uses: actions/deploy-pages@v2
```

> [!WARNING]
> You'll need to change `path: './generated'` if you overridden `dist_path` in your `config.ini` file. 
