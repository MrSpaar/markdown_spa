function overrideLinks() {
    for (let a of document.getElementsByTagName('a')) {
        a.target = '_blank';

        if (a.href.startsWith(window.location.origin)) {
            a.addEventListener('click', e => {
                e.preventDefault();
                update(a.href);
                window.history.pushState({}, '', a.href);
            });
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
    console.log("popstate");
    update(window.location.href);
});

overrideLinks();