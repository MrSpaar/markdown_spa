function prepare() {
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
    fetch(path)
        .then(resp => resp.text())
        .then(html => {
            document.documentElement.innerHTML = html;
            if (push)
                window.history.pushState({}, '', path);
            prepare();
        });
}

prepare();
let curPath = window.location.pathname;

window.addEventListener('popstate', _ => {
    if (window.location.pathname != curPath) {
        update(window.location.href, false);
        curPath = window.location.pathname;
    }
});
