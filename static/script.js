function prepare() {
    document.getElementById('show-nav-label').onkeydown = e => {
        if (e.key == 'Enter')
            e.target.children[0].click();
    };

    for (let a of document.getElementsByTagName('a')) {
        if ((a.href.baseVal || a.href).startsWith(window.location.origin)) {
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

    fetch(path)
        .then(resp => resp.text())
        .then(html => {
            document.documentElement.innerHTML = html;
            if (push)
                window.history.pushState({}, '', path);
            prepare();
        })
        .catch(_ => {
            const error = document.getElementById('error');
            error.classList.add('active');

            setTimeout(_ => {
                error.classList.remove('active');
            }, 2000);
        });
}

prepare();
window.addEventListener('popstate', _ => {
    update(window.location.href, false);
});
