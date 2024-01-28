if (typeof preFetch !== 'function') { function preFetch() {} }
if (typeof postFetch !== 'function') { function postFetch() {} }

function overrideLinks() {
    document.querySelectorAll('a').forEach(a => {
        if (a.href.startsWith(window.location.origin) && !a.hasAttribute('onclick')) {
            a.onclick = e => {
                e.preventDefault();
                updatePage(a.href);
            };
        }
    });
}

async function updatePage(path) {
    preFetch();

    if (typeof updateWithJSON === 'function') {
        updateWithJSON(await fetch(path+'index.json').then(r => r.json()));
    } else {
        let text = await fetch(path).then(r => r.text());
        document.documentElement.innerHTML = text;
    }

    overrideLinks();
    postFetch();

    window.history.pushState({}, '', path);
}

postFetch();
overrideLinks();

let curPath = window.location.pathname;

window.addEventListener('popstate', async _ => {
    if (window.location.pathname == curPath) {
        return;
    }

    curPath = window.location.pathname;
    await updatePage(window.location.href);
});
