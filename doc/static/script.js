function prepare() {
    for (let h2 of document.getElementsByTagName('h2')) {
        h2.classList.add('anchor');
        h2.id = h2.innerText.toLowerCase().replace(/[^a-z0-9]/g, '-');

        h2.addEventListener('click', e => {
            e.target.scrollIntoView();
            history.pushState({}, '', `#${h2.id}`);
            navigator.clipboard.writeText(`${window.location.origin}${window.location.pathname}#${h2.id}`);
        });
    }
}

function update(path, push = true) {
    let loader = document.getElementById('loader');
    loader.classList.add('active');

    fetch(path + "index.json")
        .then(resp => resp.json())
        .then(json => {
            document.title = `Markdown SPA - ${json.name}`;
            document.querySelector('meta[name="description"]').content = json.description;

            document.querySelector('#content').innerHTML = `<h1>${json.name}</h1>${json.page_content}`

            if (push)
                window.history.pushState({}, '', path);

            prepare();
            loader.classList.remove('active');
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
