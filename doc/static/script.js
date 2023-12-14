function prepare() {
    document.getElementById('show-nav-label').onkeydown = e => {
        if (e.key == 'Enter')
            e.target.children[0].click();
    };

    for (let h2 of document.getElementsByTagName('h2')) {
        h2.classList.add('anchor');
        h2.id = h2.innerText.toLowerCase().replace(/[^a-z0-9]/g, '-');

        h2.addEventListener('click', e => {
            e.target.scrollIntoView();
            history.pushState({}, '', `#${h2.id}`);
            navigator.clipboard.writeText(`${window.location.origin}${window.location.pathname}#${h2.id}`);
        });
    }

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
let curPath = window.location.pathname;

window.addEventListener('popstate', _ => {
    if (window.location.pathname != curPath) {
        update(window.location.href, false);
        curPath = window.location.pathname;
    }
});
