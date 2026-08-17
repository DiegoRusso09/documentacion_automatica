let currentJobId = null;

let statusInterval = null;


/*
========================================================
CONTADORES NORMALES
========================================================
*/

function updateCounter(
    inputId,
    counterId
) {

    const input =
        document.getElementById(
            inputId
        );

    const counter =
        document.getElementById(
            counterId
        );

    if (
        !input ||
        !counter
    ) {
        return;
    }

    input.addEventListener(
        "change",
        () => {

            counter.textContent =
                input.files.length;
        }
    );
}


updateCounter(
    "vb_files",
    "vb_count"
);

updateCounter(
    "apex_files",
    "apex_count"
);

updateCounter(
    "bip_files",
    "bip_count"
);

updateCounter(
    "sql_files",
    "sql_count"
);


/*
========================================================
OIC DROPZONE
========================================================
*/

const oicDropzone =
    document.getElementById(
        "oic_dropzone"
    );

const oicFileInput =
    document.getElementById(
        "oic_files"
    );

const oicFileList =
    document.getElementById(
        "oic_file_list"
    );

const oicLocalCount =
    document.getElementById(
        "oic_local_count"
    );

const oicSummaryCount =
    document.getElementById(
        "oic_count"
    );


let oicSelectedFiles = [];


/*
========================================================
VALIDAR QUE OIC EXISTA
========================================================
*/

if (
    oicDropzone &&
    oicFileInput &&
    oicFileList
) {

    /*
    ====================================================
    CLICK
    ====================================================
    */

    oicDropzone.addEventListener(
        "click",
        () => {

            oicFileInput.click();
        }
    );


    /*
    ====================================================
    SELECCIÓN MEDIANTE EXPLORADOR
    ====================================================
    */

    oicFileInput.addEventListener(
        "change",
        event => {

            addOicFiles(
                event.target.files
            );

            /*
            Permitimos volver a seleccionar
            el mismo archivo posteriormente.
            */

            oicFileInput.value = "";
        }
    );


    /*
    ====================================================
    DRAG OVER
    ====================================================
    */

    oicDropzone.addEventListener(
        "dragover",
        event => {

            event.preventDefault();

            event.stopPropagation();

            oicDropzone.classList.add(
                "dragover"
            );
        }
    );


    /*
    ====================================================
    DRAG ENTER
    ====================================================
    */

    oicDropzone.addEventListener(
        "dragenter",
        event => {

            event.preventDefault();

            event.stopPropagation();

            oicDropzone.classList.add(
                "dragover"
            );
        }
    );


    /*
    ====================================================
    DRAG LEAVE
    ====================================================
    */

    oicDropzone.addEventListener(
        "dragleave",
        event => {

            event.preventDefault();

            event.stopPropagation();

            oicDropzone.classList.remove(
                "dragover"
            );
        }
    );


    /*
    ====================================================
    DROP
    ====================================================
    */

    oicDropzone.addEventListener(
        "drop",
        event => {

            event.preventDefault();

            event.stopPropagation();

            oicDropzone.classList.remove(
                "dragover"
            );

            addOicFiles(
                event.dataTransfer.files
            );
        }
    );
}


/*
========================================================
AGREGAR ARCHIVOS OIC
========================================================
*/

function addOicFiles(files) {

    for (
        const file of files
    ) {

        const extension =
            file.name
                .split(".")
                .pop()
                .toLowerCase();


        /*
        Solo permitimos .PAR y .IAR
        */

        if (
            extension !== "par" &&
            extension !== "iar"
        ) {

            continue;
        }


        /*
        Evitar duplicados
        */

        const exists =
            oicSelectedFiles.some(

                existing =>

                    existing.name ===
                    file.name

                    &&

                    existing.size ===
                    file.size
            );


        if (!exists) {

            oicSelectedFiles.push(
                file
            );
        }
    }


    renderOicFiles();
}


/*
========================================================
ELIMINAR ARCHIVO OIC
========================================================
*/

function removeOicFile(
    index
) {

    oicSelectedFiles.splice(
        index,
        1
    );

    renderOicFiles();
}


/*
========================================================
RENDERIZAR LISTA OIC
========================================================
*/

function renderOicFiles() {

    if (!oicFileList) {

        return;
    }


    oicFileList.innerHTML =
        "";


    if (
        oicSelectedFiles.length === 0
    ) {

        oicFileList.innerHTML = `

            <div class="oic-empty-message">

                No hay archivos seleccionados

            </div>

        `;

    } else {

        oicSelectedFiles.forEach(
            (
                file,
                index
            ) => {

                const div =
                    document.createElement(
                        "div"
                    );


                div.className =
                    "oic-file-item";


                div.innerHTML = `

                    <div class="oic-file-info">

                        <strong>
                            ${index + 1}.
                        </strong>

                        ${file.name}

                        <br>

                        ${(
                            file.size /
                            1024
                        ).toFixed(2)} KB

                    </div>

                    <button
                        type="button"
                        class="oic-remove-btn"
                        onclick="removeOicFile(${index})"
                    >

                        ✖

                    </button>

                `;


                oicFileList.appendChild(
                    div
                );
            }
        );
    }


    if (oicLocalCount) {

        oicLocalCount.textContent =
            oicSelectedFiles.length;
    }


    if (oicSummaryCount) {

        oicSummaryCount.textContent =
            oicSelectedFiles.length;
    }
}


/*
========================================================
GENERAR DS140
========================================================
*/

async function generateDS140() {

    try {

        const button =
            document.querySelector(
                ".generate-btn"
            );


        button.disabled =
            true;


        button.innerText =
            "Generando...";


        const progressContainer =
            document.getElementById(
                "progress-container"
            );


        const progressBar =
            document.getElementById(
                "progress-bar"
            );


        const progressText =
            document.getElementById(
                "progress-text"
            );


        progressContainer.style.display =
            "block";


        progressBar.style.width =
            "0%";


        progressText.innerText =
            "Iniciando...";


        /*
        ====================================================
        FORM DATA
        ====================================================
        */

        const formData =
            new FormData();


        formData.append(

            "author_name",

            document.getElementById(
                "author_name"
            ).value
        );


        formData.append(

            "development_name",

            document.getElementById(
                "development_name"
            ).value
        );


        /*
        ====================================================
        VISUAL BUILDER
        ====================================================
        */

        const vbInput =
            document.getElementById(
                "vb_files"
            );


        if (vbInput) {

            for (
                const file of vbInput.files
            ) {

                formData.append(
                    "vb_files",
                    file
                );
            }
        }


        /*
        ====================================================
        APEX
        ====================================================
        */

        const apexInput =
            document.getElementById(
                "apex_files"
            );


        if (apexInput) {

            for (
                const file of apexInput.files
            ) {

                formData.append(
                    "apex_files",
                    file
                );
            }
        }


        /*
        ====================================================
        OIC
        ====================================================
        */

        for (
            const file of oicSelectedFiles
        ) {

            formData.append(
                "oic_files",
                file
            );
        }


        /*
        ====================================================
        BI PUBLISHER
        ====================================================
        */

        const bipInput =
            document.getElementById(
                "bip_files"
            );


        if (bipInput) {

            for (
                const file of bipInput.files
            ) {

                formData.append(
                    "bip_files",
                    file
                );
            }
        }


        /*
        ====================================================
        SQL
        ====================================================
        */

        const sqlInput =
            document.getElementById(
                "sql_files"
            );


        if (sqlInput) {

            for (
                const file of sqlInput.files
            ) {

                formData.append(
                    "sql_files",
                    file
                );
            }
        }


        /*
        ====================================================
        START
        ====================================================
        */

        const response =
            await fetch(

                "/api/ds140/start",

                {
                    method: "POST",
                    body: formData
                }
            );


        if (!response.ok) {

            const errorText =
                await response.text();


            throw new Error(

                "Error iniciando proceso: " +
                errorText
            );
        }


        const result =
            await response.json();


        currentJobId =
            result.job_id;


        statusInterval =
            setInterval(

                checkStatus,

                1000
            );

    }

    catch (error) {

        console.error(
            error
        );


        alert(
            error.message
        );


        resetButton();
    }
}


/*
========================================================
STATUS
========================================================
*/

async function checkStatus() {

    if (!currentJobId) {

        return;
    }


    const response =
        await fetch(

            `/api/ds140/status/${currentJobId}`
        );


    const job =
        await response.json();


    const progress =
        job.progress || 0;


    const component =
        job.step || "";


    const activity =
        job.activity || "";


    const objectName =
        job.object || "";


    const current =
        job.current || 0;


    const total =
        job.total || 0;


    document.getElementById(
        "progress-bar"
    ).style.width =
        progress + "%";


    document.getElementById(
        "progress-text"
    ).innerText =
        `${progress}% - ${component}`;


    document.getElementById(
        "activity-text"
    ).innerText =
        activity;


    document.getElementById(
        "detail-text"
    ).innerText =
        `${objectName} (${current}/${total})`;


    /*
    ====================================================
    COMPLETED
    ====================================================
    */

    if (
        job.status === "completed"
    ) {

        clearInterval(
            statusInterval
        );


        window.location.href =

            `/api/ds140/download/${currentJobId}`;


        resetButton();
    }


    /*
    ====================================================
    ERROR
    ====================================================
    */

    if (
        job.status === "error"
    ) {

        clearInterval(
            statusInterval
        );


        alert(
            job.error
        );


        resetButton();
    }
}


/*
========================================================
RESET BUTTON
========================================================
*/

function resetButton() {

    const button =
        document.querySelector(
            ".generate-btn"
        );


    if (!button) {

        return;
    }


    button.disabled =
        false;


    button.innerText =
        "Generar Documento DS140";
}