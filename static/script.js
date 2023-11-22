function overrideLinks() {
    for (let a of document.querySelectorAll('a')) {
        if (a.href.startsWith(window.location.origin)) {
            a.addEventListener('pointerdown', changePage);
        }
    }
}

function changePage(event) {
    event.preventDefault();

    fetch(`${event.target.href}`)
        .then(resp => resp.text())
        .then(html => {
            let start = html.indexOf('<body>') + 6;
            let end = html.lastIndexOf('</body>');

            document.body.innerHTML = html.substring(start, end);
            overrideLinks();
        });

    window.history.pushState({}, '', event.target.href);
}

overrideLinks();
