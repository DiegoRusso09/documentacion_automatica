async function loadPage(page)
{
    try
    {
        const version =
            Date.now();

        const response =
            await fetch(
                `/static/pages/${page}.html?v=${version}`,
                {
                    cache: "no-store"
                }
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
            .innerHTML =
            html;

        await loadPageScripts(
            page,
            version
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
    page,
    version
)
{
    return new Promise(
        resolve =>
        {
            const oldScripts =
                document.querySelectorAll(
                    ".dynamic-page-script"
                );

            oldScripts.forEach(
                script =>
                script.remove()
            );

            const script =
                document.createElement(
                    "script"
                );

            script.src =
                `/static/js/${page}.js?v=${version}`;

            script.classList.add(
                "dynamic-page-script"
            );

            script.onload =
                () =>
                {
                    console.log(
                        `[ROUTER] ${page}.js cargado`
                    );

                    resolve();
                };

            script.onerror =
                () =>
                {
                    console.warn(
                        `No existe ${page}.js`
                    );

                    resolve();
                };

            document.body.appendChild(
                script
            );
        }
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