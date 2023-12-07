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

    for (let pre of document.getElementsByTagName('pre')) {
        pre.setAttribute('tabindex', '0');
        pre.setAttribute('role', 'code');
    }

    for (let table of document.getElementsByTagName('table')) {
        table.setAttribute('tabindex', '0');
        table.setAttribute('role', 'table');
    }
}

function update(path, push = true) {
    document.getElementById('loader').classList.add('active');

    fetch(path)
        .then(resp => resp.text())
        .then(html => {
            document.documentElement.innerHTML = html;
            if (push)
                window.history.pushState({}, '', path);
            overrideLinks();
        })
        .catch(_ => {
            const error = document.getElementById('error');
            error.classList.add('active');

            setTimeout(_ => {
                error.classList.remove('active');
            }, 2000);
        });
}

overrideLinks();
window.addEventListener('popstate', _ => {
    update(window.location.href, false);
});
