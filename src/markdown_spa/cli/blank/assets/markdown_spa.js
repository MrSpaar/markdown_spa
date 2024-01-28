if (typeof preFetch !== 'function') { function preFetch() {} }
if (typeof postFetch !== 'function') { function postFetch() {} }

async function updatePage(path) {
    preFetch();

    if (typeof updateWithJSON === 'function') {
        updateWithJSON(await fetch(path+'index.json').then(r => r.json()));
    } else {
        let text = await fetch(path).then(r => r.text());
        document.documentElement.innerHTML = text;
    }

    window.history.pushState({}, '', path);
    postFetch();
}

postFetch();
let curPath = window.location.pathname;

window.addEventListener('popstate', async _ => {
    if (window.location.pathname == curPath) {
        return;
    }

    curPath = window.location.pathname;
    await updatePage(window.location.href);
});

window.addEventListener('click', e => {
    if (e.target.tagName == 'A' && e.target.href.startsWith(window.location.origin)) {
        e.preventDefault();

        if (e.target.href != window.location.href)
            updatePage(e.target.href);
    }
});
