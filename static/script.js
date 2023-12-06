function overrideLinks() {
    for (let a of document.getElementsByTagName('a')) {
        let link = a.href.baseVal || a.href;

        if (link.startsWith(window.location.origin)) {
            a.addEventListener('click', e => {
                e.preventDefault();
                update(a.href);
            });
        }
    }
}

function update(path) {
    if (path === window.location.href) {
        return;
    }

    path = path || window.location.href;
    document.getElementById('loader').classList.add('active');;

    fetch(path)
        .then(resp => resp.text())
        .then(html => {
            let start = html.indexOf('<body>') + 6;
            let end = html.lastIndexOf('</body>');

            document.body.innerHTML = html.substring(start, end);
            overrideLinks();
            window.history.pushState({}, '', a.href);
        });
}

overrideLinks();
window.addEventListener('popstate', _ => {
    update();
});
