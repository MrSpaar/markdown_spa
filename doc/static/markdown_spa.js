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
    if (!e.target.hasAttribute("href")) {
        return;
    }

    if (e.target.href.startsWith(window.location.origin)) {
        e.preventDefault();
        updatePage(e.target.href);
        window.history.pushState({}, '', e.target.href);
    }
})
