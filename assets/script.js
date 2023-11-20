async function renderFile(path) {
    const app = document.getElementById('app')
    app.innerHTML = '';

    fetch(`generated/pages/${path}.html`)
        .then(res => res.text())
        .then(html => { app.innerHTML += html; });
}

(function overrideLinks() {
    document.querySelectorAll('a').forEach(a => {
        a.addEventListener('click', e => {
            e.preventDefault();    
            let path = e.target.href.slice(e.target.href.lastIndexOf('pages/')+6);
    
            renderFile(path);
            window.history.pushState({}, '', "#/"+path);
        }
    )});
})();

(async function renderCurrent() {
    let pos = window.location.href.lastIndexOf('#/');

    renderFile((pos === -1) ?
        "index" : window.location.href.slice(pos + 2)
    );
})();
