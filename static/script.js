function overrideLinks() {
    for (let a of document.getElementsByTagName('a')) {
        let link = a.href.baseVal || a.href;

        if (link.startsWith(window.location.origin)) {
            a.addEventListener('click', e => {
                e.preventDefault();

                if (a.href == window.location.href) {
                    return;
                }

                update(a.href);
                window.history.pushState({}, '', a.href);
            });
        }
    }
}

function update(path) {
    document.getElementById('loader').classList.add('active');;

    fetch(path)
        .then(resp => resp.text())
        .then(html => {
            document.documentElement.innerHTML = html;
            overrideLinks();
        });
}

overrideLinks();
window.addEventListener('popstate', _ => {
    update(window.location.href);
});
