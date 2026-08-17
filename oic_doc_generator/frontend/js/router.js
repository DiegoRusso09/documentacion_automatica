async function loadPage(page)
{
    try
    {
        /*
        ====================================================
        CACHE BUSTER
        ====================================================
        */

        const version =
            Date.now();


        /*
        ====================================================
        LOAD HTML
        ====================================================
        */

        const response =
            await fetch(

                `/static/pages/${page}.html?v=${version}`,

                {
                    method: "GET",
                    cache: "no-store",

                    headers: {
                        "Cache-Control": "no-cache"
                    }
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


        const app =
            document.getElementById(
                "app"
            );


        if (!app)
        {
            throw new Error(
                "No existe el contenedor #app"
            );
        }


        /*
        ====================================================
        REPLACE PAGE
        ====================================================
        */

        app.innerHTML =
            html;


        /*
        ====================================================
        LOAD PAGE JS
        ====================================================
        */

        await loadPageScripts(
            page,
            version
        );
    }

    catch(error)
    {
        console.error(
            "[ROUTER]",
            error
        );


        const app =
            document.getElementById(
                "app"
            );


        if (app)
        {
            app.innerHTML =

            `
            <div style="padding:20px">

                Error cargando página:

                ${error.message}

            </div>
            `;
        }
    }
}


/*
========================================================
LOAD JAVASCRIPT
========================================================
*/

function loadPageScripts(
    page,
    version
)
{
    return new Promise(

        resolve =>
        {
            /*
            =================================================
            REMOVE PREVIOUS DYNAMIC SCRIPT
            =================================================
            */

            const oldScripts =
                document.querySelectorAll(
                    ".dynamic-page-script"
                );


            oldScripts.forEach(
                script =>
                {
                    script.remove();
                }
            );


            /*
            =================================================
            CREATE NEW SCRIPT
            =================================================
            */

            const script =
                document.createElement(
                    "script"
                );


            script.src =
                `/static/js/${page}.js?v=${version}`;


            script.classList.add(
                "dynamic-page-script"
            );


            /*
            =================================================
            SCRIPT LOADED
            =================================================
            */

            script.onload =
                () =>
                {
                    console.log(
                        `[ROUTER] ${page}.js cargado`,
                        version
                    );

                    resolve();
                };


            /*
            =================================================
            SCRIPT NOT FOUND
            =================================================
            */

            script.onerror =
                () =>
                {
                    console.warn(
                        `[ROUTER] No se pudo cargar ${page}.js`
                    );

                    resolve();
                };


            /*
            =================================================
            APPEND SCRIPT
            =================================================
            */

            document.body.appendChild(
                script
            );
        }
    );
}


/*
========================================================
ROUTE
========================================================
*/

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


    console.log(
        "[ROUTER] Cargando:",
        page
    );


    loadPage(
        page
    );
}


/*
========================================================
HASH CHANGE
========================================================
*/

window.addEventListener(
    "hashchange",
    route
);


/*
========================================================
INITIAL LOAD
========================================================
*/

route();