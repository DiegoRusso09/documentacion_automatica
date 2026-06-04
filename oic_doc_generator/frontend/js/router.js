async function loadPage(page)
{
    const response =
        await fetch(
            `pages/${page}.html`
        );

    const html =
        await response.text();

    document
        .getElementById(
            "app"
        )
        .innerHTML = html;
}

window.addEventListener(
    "hashchange",
    route
);

function route()
{
    const page =
        location.hash
            .replace("#","")
        ||
        "home";

    loadPage(page);
}

route();