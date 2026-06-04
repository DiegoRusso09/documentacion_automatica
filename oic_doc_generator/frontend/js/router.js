async function loadPage(page)
{
    try
    {
        const response =
            await fetch(

                `/static/pages/${page}.html`
            );

        if (!response.ok)
        {
            throw new Error(
                `No se pudo cargar ${page}.html`
            );
        }

        const html =
            await response.text();

        document
            .getElementById(
                "app"
            )
            .innerHTML = html;

        loadPageScripts(
            page
        );
    }

    catch(error)
    {
        console.error(
            error
        );

        document
            .getElementById(
                "app"
            )
            .innerHTML =

            `
            <div style="padding:20px">
                Error cargando página:
                ${error.message}
            </div>
            `;
    }
}


function loadPageScripts(
    page
)
{
    const oldScripts =

        document.querySelectorAll(
            ".dynamic-page-script"
        );

    oldScripts.forEach(

        script => script.remove()
    );

    const script =
        document.createElement(
            "script"
        );

    script.src =
        `/static/js/${page}.js`;

    script.classList.add(
        "dynamic-page-script"
    );

    script.onerror = () =>
    {
        console.warn(
            `No existe ${page}.js`
        );
    };

    document.body.appendChild(
        script
    );
}


window.addEventListener(

    "hashchange",

    route
);


function route()
{
    const page =

        location.hash
            .replace(
                "#",
                ""
            )

        ||

        "home";

    loadPage(
        page
    );
}


route();