function overrideLinks() {
    for (let a of document.getElementsByTagName('a')) {
        let link = a.href.baseVal || a.href;

        if (link.startsWith(window.location.origin)) {
            a.addEventListener('click', e => {
                e.preventDefault();
                if (a.href != window.location.href)
                    update(a.href);
            });
        }
    }
}

function update(path, push = true) {
    document.getElementById('loader').classList.add('active');

    if (path[path.length - 1] != '/')
        path += '/';

    fetch(path)
        .then(resp => resp.text())
        .then(html => {
            document.documentElement.innerHTML = html;
            if (push)
                window.history.pushState({}, '', path);
            overrideLinks();
        });
}

overrideLinks();
window.addEventListener('popstate', _ => {
    update(window.location.href, false);
});
