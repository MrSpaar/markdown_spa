let loader = document.getElementById('loader');
let input = document.getElementById('show-nav')

function preFetch() {
    loader.classList.add('active');
}

function updateWithJSON(json) {
    document.title = `Markdown SPA - ${json.name}`;
    document.querySelector('meta[name="description"]').content = json.description;
    document.querySelector('#content').innerHTML = `<h1>${json.name}</h1>${json.page_content}`
}

function postFetch() {
    for (let h2 of document.getElementsByName('h2')) {
        h2.classList.add('anchor');
        h2.id = h2.innerText.toLowerCase().replace(/[^a-z0-9]/g, '-');

        h2.addEventListener('click', e => {
            e.target.scrollIntoView();
            history.pushState({}, '', `#${h2.id}`);
            navigator.clipboard.writeText(`${window.location.origin}${window.location.pathname}#${h2.id}`);
        });
    }

    loader.classList.remove('active');
    input.checked = false;
}
