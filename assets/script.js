const app = document.getElementById('app')

function changePage(event) {
    event.preventDefault();

    fetch(`${event.target.href}`)
        .then(resp => resp.text())
        .then(html => {
            app.innerHTML = html.split('<div id="app">')[1].split('</div>')[0];
        });

    window.history.pushState({}, '', event.target.href);
}

document.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', changePage)
});
