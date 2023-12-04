function overrideLinks() {
    for (let a of document.getElementsByTagName('a')) {
        let link = a.href.baseVal || a.href;

        if (link.startsWith(window.location.origin)) {
            a.addEventListener('click', e => {
                e.preventDefault();
                update(a.href);
                window.history.pushState({}, '', a.href);
            });
        } else {
            a.target = '_blank';
        }
    }
}

function update(path) {
    fetch(path)
        .then(resp => resp.text())
        .then(html => {
            let start = html.indexOf('<body>') + 6;
            let end = html.lastIndexOf('</body>');

            document.body.innerHTML = html.substring(start, end);
            overrideLinks();
        });
}

window.addEventListener('popstate', e => {
    update(window.location.href);
});

overrideLinks();