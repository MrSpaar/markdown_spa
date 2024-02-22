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
    let targetAnchor = e.target.closest('a');
    if (!targetAnchor || !targetAnchor.hasAttribute("href")) {
        return;
    }

    href = (targetAnchor) ? targetAnchor.href : e.target.href;
    e.preventDefault();

    if (href == window.location.href) {
        return;
    }

    if (href.startsWith(window.location.origin)) {
        e.preventDefault();
        updatePage(href);
        window.history.pushState({}, '', href);
    }
})
