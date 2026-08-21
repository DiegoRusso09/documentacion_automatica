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
    // FILE STORE
    // =====================================================

    const fileStore = {

        vb: [],

        apex: [],

        oic: [],

        bip: [],

        sql: []
    };


    // =====================================================
    // CONFIGURACIÓN DE COMPONENTES
    // =====================================================

    const componentConfig = {

        vb: {

            sectionId:
                "sec-vb",

            inputId:
                "vb_files",

            summaryCounterId:
                "vb_count",

            parameterName:
                "vb_files",

            allowedExtensions:
                [
                    "zip"
                ]
        },


        apex: {

            sectionId:
                "sec-apex",

            inputId:
                "apex_files",

            summaryCounterId:
                "apex_count",

            parameterName:
                "apex_files",

            /*
             * El HTML original no tenía
             * restricción de extensión.
             */
            allowedExtensions:
                null
        },


        oic: {

            sectionId:
                "sec-oic",

            inputId:
                "oic_files",

            summaryCounterId:
                "oic_count",

            parameterName:
                "oic_files",

            allowedExtensions:
                [
                    "par",
                    "iar"
                ]
        },


        bip: {

            sectionId:
                "sec-bip",

            inputId:
                "bip_files",

            summaryCounterId:
                "bip_count",

            parameterName:
                "bip_files",

            allowedExtensions:
                [
                    "xdoz",
                    "xdmz",
                    "xdrz"
                ]
        },


        sql: {

            sectionId:
                "sec-sql",

            inputId:
                "sql_files",

            summaryCounterId:
                "sql_count",

            parameterName:
                "sql_files",

            allowedExtensions:
                [
                    "sql"
                ]
        }

    };


    // =====================================================
    // INICIALIZAR DROPZONE
    // =====================================================

    function initDropzone(
        storeKey
    ) {

        const config =
            componentConfig[
                storeKey
            ];


        const section =
            document.getElementById(
                config.sectionId
            );


        if (!section) {

            console.error(
                `[DS140] No existe #${config.sectionId}`
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


        const summaryCounter =
            document.getElementById(
                config.summaryCounterId
            );


        const selectedFiles =
            fileStore[
                storeKey
            ];


        if (
            !dropzone ||
            !fileInput ||
            !fileList ||
            !counter
        ) {

            console.error(
                `[DS140] Estructura incompleta: ${storeKey}`,
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
            `[DS140] Dropzone ${storeKey} inicializado`
        );


        // =================================================
        // CLICK
        // =================================================

        dropzone.addEventListener(
            "click",
            () => {

                fileInput.click();
            }
        );


        // =================================================
        // FILE SELECTOR
        // =================================================

        fileInput.addEventListener(
            "change",
            event => {

                addFiles(
                    event.target.files
                );


                /*
                 * Permite seleccionar nuevamente
                 * el mismo archivo.
                 */
                fileInput.value =
                    "";
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


                addFiles(
                    event.dataTransfer.files
                );
            }
        );


        // =================================================
        // AGREGAR ARCHIVOS
        // =================================================

        function addFiles(
            files
        ) {

            for (
                const file of files
            ) {

                // =========================================
                // EXTENSIÓN
                // =========================================

                const extension =
                    getFileExtension(
                        file.name
                    );


                // =========================================
                // VALIDAR EXTENSIÓN
                // =========================================

                if (
                    config.allowedExtensions &&
                    !config.allowedExtensions.includes(
                        extension
                    )
                ) {

                    console.warn(
                        `[DS140] Archivo rechazado en ${storeKey}:`,
                        file.name
                    );


                    continue;
                }


                // =========================================
                // EVITAR DUPLICADOS
                // =========================================

                const exists =
                    selectedFiles.some(

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

                    selectedFiles.push(
                        file
                    );
                }
            }


            renderFiles();
        }


        // =================================================
        // RENDERIZAR
        // =================================================

        function renderFiles() {

            fileList.innerHTML =
                "";


            // =============================================
            // SIN ARCHIVOS
            // =============================================

            if (
                selectedFiles.length === 0
            ) {

                fileList.innerHTML = `

                    <div class="empty-message">

                        No hay archivos seleccionados

                    </div>

                `;


                counter.textContent =
                    "0";


                if (summaryCounter) {

                    summaryCounter.textContent =
                        "0";
                }


                return;
            }


            // =============================================
            // ARCHIVOS
            // =============================================

            selectedFiles.forEach(
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


                    // =====================================
                    // INFO
                    // =====================================

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

                        ${escapeHtml(
                            file.name
                        )}

                        <br>

                        ${formatFileSize(
                            file.size
                        )}

                    `;


                    // =====================================
                    // REMOVE BUTTON
                    // =====================================

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


                    removeButton.title =
                        "Eliminar archivo";


                    removeButton.addEventListener(
                        "click",
                        event => {

                            event.preventDefault();

                            event.stopPropagation();


                            selectedFiles.splice(
                                index,
                                1
                            );


                            renderFiles();
                        }
                    );


                    // =====================================
                    // APPEND
                    // =====================================

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


            // =============================================
            // COUNTERS
            // =============================================

            counter.textContent =
                selectedFiles.length;


            if (summaryCounter) {

                summaryCounter.textContent =
                    selectedFiles.length;
            }


            console.log(
                `[DS140] ${storeKey}: ${selectedFiles.length} archivo(s)`
            );
        }


        // =================================================
        // INITIAL RENDER
        // =================================================

        renderFiles();
    }


    // =====================================================
    // EXTENSIÓN
    // =====================================================

    function getFileExtension(
        fileName
    ) {

        const position =
            fileName.lastIndexOf(
                "."
            );


        if (
            position === -1
        ) {

            return "";
        }


        return fileName
            .substring(
                position + 1
            )
            .toLowerCase();
    }


    // =====================================================
    // FORMAT FILE SIZE
    // =====================================================

    function formatFileSize(
        bytes
    ) {

        if (
            bytes < 1024
        ) {

            return `${bytes} B`;
        }


        if (
            bytes <
            1024 * 1024
        ) {

            return `${(
                bytes / 1024
            ).toFixed(2)} KB`;
        }


        return `${(
            bytes /
            1024 /
            1024
        ).toFixed(2)} MB`;
    }


    // =====================================================
    // ESCAPE HTML
    // =====================================================

    function escapeHtml(
        value
    ) {

        const div =
            document.createElement(
                "div"
            );


        div.textContent =
            value;


        return div.innerHTML;
    }


    // =====================================================
    // AGREGAR ARCHIVOS A FORMDATA
    // =====================================================

    function appendStoredFiles(
        formData,
        storeKey
    ) {

        const config =
            componentConfig[
                storeKey
            ];


        const files =
            fileStore[
                storeKey
            ];


        for (
            const file of files
        ) {

            formData.append(
                config.parameterName,
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


            // =================================================
            // PROGRESS
            // =================================================

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
            // FORMDATA
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
            // FILES
            // =================================================

            appendStoredFiles(
                formData,
                "vb"
            );


            appendStoredFiles(
                formData,
                "apex"
            );


            appendStoredFiles(
                formData,
                "oic"
            );


            appendStoredFiles(
                formData,
                "bip"
            );


            appendStoredFiles(
                formData,
                "sql"
            );


            console.log(
                "[DS140] Archivos a enviar:",
                {
                    vb:
                        fileStore.vb.length,

                    apex:
                        fileStore.apex.length,

                    oic:
                        fileStore.oic.length,

                    bip:
                        fileStore.bip.length,

                    sql:
                        fileStore.sql.length
                }
            );


            // =================================================
            // START
            // =================================================

            const response =
                await fetch(

                    "/api/ds140/start",

                    {
                        method:
                            "POST",

                        body:
                            formData
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
                job.status ===
                "completed"
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
    // INITIALIZACIÓN DE DROPZONES
    // =====================================================

    initDropzone(
        "vb"
    );


    initDropzone(
        "apex"
    );


    initDropzone(
        "oic"
    );


    initDropzone(
        "bip"
    );


    initDropzone(
        "sql"
    );


    console.log(
        "[DS140] Inicialización completa"
    );

})();