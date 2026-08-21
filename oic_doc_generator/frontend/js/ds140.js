(() => {

    console.log(
        "[DS140] ds140.js ejecutado"
    );


    // =====================================================
    // VARIABLES DEL PROCESO
    // =====================================================

    let currentJobId = null;

    let statusInterval = null;


    // =====================================================
    // OIC FILE STORE
    // =====================================================

    const oicSelectedFiles = [];


    // =====================================================
    // CONTADORES TRADICIONALES
    // =====================================================

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


    // =====================================================
    // OIC DROPZONE
    // =====================================================

    function initOicDropzone() {

        const section =
            document.getElementById(
                "sec-oic"
            );


        if (!section) {

            console.error(
                "[DS140] No existe #sec-oic"
            );

            return;
        }


        const dropzone =
            section.querySelector(
                ".dropzone"
            );


        const fileInput =
            section.querySelector(
                ".fileInput"
            );


        const fileList =
            section.querySelector(
                ".file-list"
            );


        const counter =
            section.querySelector(
                ".counter-val"
            );


        if (
            !dropzone ||
            !fileInput ||
            !fileList ||
            !counter
        ) {

            console.error(
                "[DS140] Estructura OIC incompleta",
                {
                    dropzone,
                    fileInput,
                    fileList,
                    counter
                }
            );

            return;
        }


        console.log(
            "[DS140] Dropzone OIC encontrado"
        );


        // =================================================
        // CLICK
        // =================================================

        dropzone.addEventListener(
            "click",
            () => {

                console.log(
                    "[DS140] Click en OIC"
                );

                fileInput.click();
            }
        );


        // =================================================
        // SELECTOR DE ARCHIVOS
        // =================================================

        fileInput.addEventListener(
            "change",
            event => {

                console.log(
                    "[DS140] Selección OIC:",
                    event.target.files.length
                );


                addOicFiles(
                    event.target.files
                );


                /*
                 * Dejamos limpio el input para que
                 * pueda volver a seleccionarse el
                 * mismo archivo.
                 */
                fileInput.value = "";
            }
        );


        // =================================================
        // DRAG ENTER
        // =================================================

        dropzone.addEventListener(
            "dragenter",
            event => {

                event.preventDefault();

                event.stopPropagation();


                dropzone.classList.add(
                    "dragover"
                );
            }
        );


        // =================================================
        // DRAG OVER
        // =================================================

        dropzone.addEventListener(
            "dragover",
            event => {

                event.preventDefault();

                event.stopPropagation();


                event.dataTransfer.dropEffect =
                    "copy";


                dropzone.classList.add(
                    "dragover"
                );
            }
        );


        // =================================================
        // DRAG LEAVE
        // =================================================

        dropzone.addEventListener(
            "dragleave",
            event => {

                event.preventDefault();

                event.stopPropagation();


                dropzone.classList.remove(
                    "dragover"
                );
            }
        );


        // =================================================
        // DROP
        // =================================================

        dropzone.addEventListener(
            "drop",
            event => {

                event.preventDefault();

                event.stopPropagation();


                dropzone.classList.remove(
                    "dragover"
                );


                const files =
                    event.dataTransfer.files;


                console.log(
                    "[DS140] Drop OIC:",
                    files.length
                );


                addOicFiles(
                    files
                );
            }
        );


        // =================================================
        // ADD FILES
        // =================================================

        function addOicFiles(
            files
        ) {

            for (
                const file of files
            ) {

                const extension =
                    file.name
                        .split(".")
                        .pop()
                        .toLowerCase();


                // =========================================
                // VALIDAR EXTENSIÓN
                // =========================================

                if (
                    extension !== "par" &&
                    extension !== "iar"
                ) {

                    console.warn(
                        "[DS140] Archivo ignorado:",
                        file.name
                    );

                    continue;
                }


                // =========================================
                // EVITAR DUPLICADOS
                // =========================================

                const exists =
                    oicSelectedFiles.some(

                        current =>

                            current.name ===
                            file.name

                            &&

                            current.size ===
                            file.size

                            &&

                            current.lastModified ===
                            file.lastModified
                    );


                if (!exists) {

                    oicSelectedFiles.push(
                        file
                    );
                }
            }


            renderFiles();
        }


        // =================================================
        // RENDER
        // =================================================

        function renderFiles() {

            fileList.innerHTML =
                "";


            if (
                oicSelectedFiles.length === 0
            ) {

                fileList.innerHTML = `
                    <div class="empty-message">
                        No hay archivos seleccionados
                    </div>
                `;


                counter.textContent =
                    "0";


                const summaryCounter =
                    document.getElementById(
                        "oic_count"
                    );


                if (summaryCounter) {

                    summaryCounter.textContent =
                        "0";
                }


                return;
            }


            oicSelectedFiles.forEach(
                (
                    file,
                    index
                ) => {

                    const item =
                        document.createElement(
                            "div"
                        );


                    item.className =
                        "file-item";


                    const info =
                        document.createElement(
                            "div"
                        );


                    info.className =
                        "file-info";


                    info.innerHTML = `

                        <strong>
                            ${index + 1}.
                        </strong>

                        ${file.name}

                        <br>

                        ${(
                            file.size / 1024
                        ).toFixed(2)} KB
                    `;


                    const removeButton =
                        document.createElement(
                            "button"
                        );


                    removeButton.type =
                        "button";


                    removeButton.className =
                        "remove-btn";


                    removeButton.textContent =
                        "✖";


                    removeButton.addEventListener(
                        "click",
                        event => {

                            /*
                             * Evita que el click del botón
                             * vuelva a abrir el selector.
                             */

                            event.preventDefault();

                            event.stopPropagation();


                            oicSelectedFiles.splice(
                                index,
                                1
                            );


                            renderFiles();
                        }
                    );


                    item.appendChild(
                        info
                    );


                    item.appendChild(
                        removeButton
                    );


                    fileList.appendChild(
                        item
                    );
                }
            );


            counter.textContent =
                oicSelectedFiles.length;


            const summaryCounter =
                document.getElementById(
                    "oic_count"
                );


            if (summaryCounter) {

                summaryCounter.textContent =
                    oicSelectedFiles.length;
            }


            console.log(
                "[DS140] OIC almacenados:",
                oicSelectedFiles.length
            );
        }


        renderFiles();
    }


    // =====================================================
    // APPEND INPUT FILES
    // =====================================================

    function appendInputFiles(
        formData,
        inputId,
        parameterName
    ) {

        const input =
            document.getElementById(
                inputId
            );


        if (!input) {

            return;
        }


        for (
            const file of input.files
        ) {

            formData.append(
                parameterName,
                file
            );
        }
    }


    // =====================================================
    // GENERAR DS140
    // =====================================================

    async function generateDS140() {

        try {

            const button =
                document.querySelector(
                    ".generate-btn"
                );


            if (button) {

                button.disabled =
                    true;


                button.innerText =
                    "Generando...";
            }


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


            if (progressContainer) {

                progressContainer.style.display =
                    "block";
            }


            if (progressBar) {

                progressBar.style.width =
                    "0%";
            }


            if (progressText) {

                progressText.innerText =
                    "Iniciando...";
            }


            // =================================================
            // FORM DATA
            // =================================================

            const formData =
                new FormData();


            const author =
                document.getElementById(
                    "author_name"
                );


            const development =
                document.getElementById(
                    "development_name"
                );


            formData.append(
                "author_name",
                author
                    ? author.value
                    : ""
            );


            formData.append(
                "development_name",
                development
                    ? development.value
                    : ""
            );


            // =================================================
            // VISUAL BUILDER
            // =================================================

            appendInputFiles(
                formData,
                "vb_files",
                "vb_files"
            );


            // =================================================
            // APEX
            // =================================================

            appendInputFiles(
                formData,
                "apex_files",
                "apex_files"
            );


            // =================================================
            // OIC
            // =================================================

            for (
                const file of oicSelectedFiles
            ) {

                formData.append(
                    "oic_files",
                    file
                );
            }


            // =================================================
            // BI PUBLISHER
            // =================================================

            appendInputFiles(
                formData,
                "bip_files",
                "bip_files"
            );


            // =================================================
            // SQL
            // =================================================

            appendInputFiles(
                formData,
                "sql_files",
                "sql_files"
            );


            console.log(
                "[DS140] Enviando:",
                {
                    oic:
                        oicSelectedFiles.length
                }
            );


            // =================================================
            // START
            // =================================================

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
                    `Error iniciando proceso (${response.status}): ${errorText}`
                );
            }


            const result =
                await response.json();


            currentJobId =
                result.job_id;


            if (statusInterval) {

                clearInterval(
                    statusInterval
                );
            }


            statusInterval =
                setInterval(

                    checkStatus,

                    1000
                );

        }
        catch(error) {

            console.error(
                "[DS140]",
                error
            );


            alert(
                error.message
            );


            resetButton();
        }
    }


    // =====================================================
    // STATUS
    // =====================================================

    async function checkStatus() {

        if (!currentJobId) {

            return;
        }


        try {

            const response =
                await fetch(

                    `/api/ds140/status/${currentJobId}`,

                    {
                        cache:
                            "no-store"
                    }
                );


            if (!response.ok) {

                throw new Error(
                    `Error consultando estado: ${response.status}`
                );
            }


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


            const progressBar =
                document.getElementById(
                    "progress-bar"
                );


            const progressText =
                document.getElementById(
                    "progress-text"
                );


            const activityText =
                document.getElementById(
                    "activity-text"
                );


            const detailText =
                document.getElementById(
                    "detail-text"
                );


            if (progressBar) {

                progressBar.style.width =
                    `${progress}%`;
            }


            if (progressText) {

                progressText.innerText =
                    `${progress}% - ${component}`;
            }


            if (activityText) {

                activityText.innerText =
                    activity;
            }


            if (detailText) {

                detailText.innerText =
                    `${objectName} (${current}/${total})`;
            }


            // =================================================
            // COMPLETED
            // =================================================

            if (
                job.status === "completed"
            ) {

                clearInterval(
                    statusInterval
                );


                statusInterval =
                    null;


                window.location.href =

                    `/api/ds140/download/${currentJobId}`;


                resetButton();


                return;
            }


            // =================================================
            // ERROR
            // =================================================

            if (
                job.status === "error" ||
                job.status === "failed"
            ) {

                clearInterval(
                    statusInterval
                );


                statusInterval =
                    null;


                alert(
                    job.error ||
                    "Error generando documento"
                );


                resetButton();
            }

        }
        catch(error) {

            console.error(
                "[DS140 STATUS]",
                error
            );
        }
    }


    // =====================================================
    // RESET BUTTON
    // =====================================================

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


    // =====================================================
    // PUBLIC FUNCTIONS
    // =====================================================

    window.generateDS140 =
        generateDS140;


    // =====================================================
    // INITIALIZE
    // =====================================================

    initOicDropzone();


    console.log(
        "[DS140] Inicialización completa"
    );

})();