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
    // APP MODAL (reemplaza a alert)
    // =====================================================
    //
    // Mismo estilo que los diálogos de la app. El tipo se
    // deduce del mensaje (error / aviso / información) si no
    // se indica.
    // =====================================================

    const MODAL_TYPES = {
        error: { icon: "✕", title: "Ocurrió un problema" },
        warning: { icon: "!", title: "Revisa la información" },
        info: { icon: "i", title: "Información" },
        success: { icon: "✓", title: "Listo" }
    };

    function guessModalType(message) {

        const text = String(message || "").toLowerCase();

        if (/error|no fue posible|fall|se perdió|se detuvo/.test(text)) {
            return "error";
        }

        if (/debe |seleccion|cargar|indicar|ingres/.test(text)) {
            return "warning";
        }

        if (/correctamente|éxito|listo|registrad/.test(text)) {
            return "success";
        }

        return "info";
    }

    function showAppModal(message, options = {}) {

        const type =
            options.type || guessModalType(message);

        const meta =
            MODAL_TYPES[type] || MODAL_TYPES.info;

        return new Promise((resolve) => {

            const overlay = document.createElement("div");

            overlay.className = "custom-dialog-overlay app-modal-overlay";

            overlay.innerHTML = `
                <div class="custom-dialog app-modal app-modal-${type}"
                     role="alertdialog" aria-modal="true">
                    <div class="app-modal-body">
                        <div class="app-modal-icon"></div>
                        <div class="app-modal-content">
                            <h3 class="app-modal-title"></h3>
                            <p class="app-modal-message"></p>
                        </div>
                    </div>
                    <div class="custom-dialog-footer">
                        <button type="button" class="dialog-primary-btn app-modal-ok">
                            Entendido
                        </button>
                    </div>
                </div>`;

            // Texto seguro (sin interpretar HTML del mensaje).
            overlay.querySelector(".app-modal-icon").textContent = meta.icon;

            overlay.querySelector(".app-modal-title").textContent =
                options.title || meta.title;

            overlay.querySelector(".app-modal-message").textContent =
                String(message ?? "");

            const close = () => {

                document.removeEventListener("keydown", onKey);

                overlay.classList.add("app-modal-closing");

                setTimeout(() => overlay.remove(), 150);

                resolve();
            };

            const onKey = (event) => {

                if (event.key === "Escape" || event.key === "Enter") {
                    event.preventDefault();
                    close();
                }
            };

            overlay.querySelector(".app-modal-ok").addEventListener("click", close);

            overlay.addEventListener("click", (event) => {
                if (event.target === overlay) {
                    close();
                }
            });

            document.addEventListener("keydown", onKey);

            document.body.appendChild(overlay);

            overlay.querySelector(".app-modal-ok").focus();
        });
    }


    // =====================================================
    // CAMPOS OBLIGATORIOS
    // =====================================================
    //
    // Un campo obligatorio vacío no bloquea la generación:
    // se envía como UNDEFINED, que se ve claramente en el
    // documento y se puede corregir después.
    // =====================================================

    const UNDEFINED_VALUE = "UNDEFINED";

    function valueOrUndefined(value) {

        const text = String(value ?? "").trim();

        return text || UNDEFINED_VALUE;
    }

    function fieldOrUndefined(id) {

        return valueOrUndefined(
            document.getElementById(id)?.value
        );
    }


    // =====================================================
    // PROGRESS ANIMATION
    // =====================================================

    let displayedProgress = 0;

    let targetProgress = 0;

    let progressAnimationFrame = null;

    // Fallos seguidos al consultar el estado. Un 502 suelto
    // (p. ej. el servidor ocupado) no debe cancelar todo.
    let statusFailures = 0;

    const MAX_STATUS_FAILURES = 8;

    // Color normal de la barra (el mismo de ds140.html).
    const PROGRESS_COLOR = "#6DBE45";


    // =====================================================
    // RESET PROGRESS STATE
    // =====================================================

    function resetProgressState() {

        displayedProgress = 0;

        targetProgress = 0;


        if (progressAnimationFrame) {

            cancelAnimationFrame(
                progressAnimationFrame
            );

            progressAnimationFrame = null;
        }


        const progressBar =
            document.getElementById(
                "progress-bar"
            );


        if (progressBar) {

            progressBar.style.width =
                "0%";
        }
    }


    // =====================================================
    // SHOW PROGRESS ERROR
    // =====================================================
    //
    // Detiene la barra, la pone en rojo y explica qué pasó,
    // para que no parezca que el proceso sigue avanzando.
    // =====================================================

    function showProgressError(message) {

        if (progressAnimationFrame) {

            cancelAnimationFrame(
                progressAnimationFrame
            );

            progressAnimationFrame = null;
        }

        const progressBar =
            document.getElementById(
                "progress-bar"
            );

        if (progressBar) {

            progressBar.style.transition =
                "none";

            progressBar.style.width =
                `${displayedProgress}%`;

            progressBar.style.background =
                "#C0392B";
        }

        const progressText =
            document.getElementById(
                "progress-text"
            );

        if (progressText) {

            progressText.innerText =
                "Error - el proceso se detuvo";
        }

        const activityText =
            document.getElementById(
                "activity-text"
            );

        if (activityText) {

            activityText.innerText =
                message;
        }

        const detailText =
            document.getElementById(
                "detail-text"
            );

        if (detailText) {

            detailText.innerText =
                "Vuelve a intentarlo. Si se repite, el servidor puede " +
                "haberse quedado sin memoria con archivos muy grandes.";
        }
    }


    function clearProgressError() {

        const progressBar =
            document.getElementById(
                "progress-bar"
            );

        // Vuelve al verde y la transición originales de la
        // barra (definidos en ds140.html).
        if (progressBar) {

            progressBar.style.background =
                PROGRESS_COLOR;

            progressBar.style.transition =
                "width .3s";
        }
    }


    // =====================================================
    // SET PROGRESS TARGET
    // =====================================================

    function setProgressTarget(
        value
    ) {

        let newTarget =
            Number(
                value
            );


        if (
            !Number.isFinite(
                newTarget
            )
        ) {

            newTarget = 0;
        }


        newTarget = Math.max(
            0,
            Math.min(
                100,
                newTarget
            )
        );


        // =================================================
        // NEVER MOVE BACKWARDS
        // =================================================

        targetProgress = Math.max(
            targetProgress,
            newTarget
        );


        if (!progressAnimationFrame) {

            progressAnimationFrame =
                requestAnimationFrame(
                    animateProgress
                );
        }
    }


    // =====================================================
    // ANIMATE PROGRESS
    // =====================================================

    function animateProgress() {

        const progressBar =
            document.getElementById(
                "progress-bar"
            );


        if (!progressBar) {

            progressAnimationFrame =
                null;

            return;
        }


        const difference =

            targetProgress
            -
            displayedProgress;


        // =================================================
        // TARGET REACHED
        // =================================================

        if (
            Math.abs(
                difference
            )
            <
            0.05
        ) {

            displayedProgress =
                targetProgress;


            progressBar.style.width =
                `${displayedProgress}%`;


            progressAnimationFrame =
                null;

            return;
        }


        // =================================================
        // SMOOTH MOVEMENT
        // =================================================
        //
        // Avanza proporcionalmente a la distancia.
        //
        // Ejemplo:
        //
        // 20 -> 35
        //
        // no salta inmediatamente a 35.
        //
        // =================================================

        let increment =
            difference * 0.08;


        // Evita que movimientos pequeños sean
        // excesivamente lentos.

        if (
            increment > 0
            &&
            increment < 0.08
        ) {

            increment = 0.08;
        }


        displayedProgress +=
            increment;


        if (
            displayedProgress
            >
            targetProgress
        ) {

            displayedProgress =
                targetProgress;
        }


        progressBar.style.width =
            `${displayedProgress}%`;


        progressAnimationFrame =
            requestAnimationFrame(
                animateProgress
            );
    }


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
                    ".doc-action-ds140"
                );


            if (button) {

                button.disabled =
                    true;


                button.classList.add(
                    "is-processing"
                );
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


            resetProgressState();


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


            const company =
                document.getElementById(
                    "company_name"
                );


            formData.append(
                "author_name",
                valueOrUndefined(author?.value)
            );


            formData.append(
                "development_name",
                valueOrUndefined(development?.value)
            );

            formData.append(
                "company_name",
                valueOrUndefined(company?.value)
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

            statusFailures = 0;

            clearProgressError();


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
        catch (error) {

            console.error(
                "[DS140]",
                error
            );


            showAppModal(
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

                const errorText =
                    await response.text();

                throw new Error(
                    `Error consultando estado (${response.status}): ${errorText}`
                );
            }


            const job =
                await response.json();

            statusFailures = 0;


            if (!job) {

                throw new Error(
                    "El backend no encontró el proceso de generación."
                );
            }


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

                setProgressTarget(
                    progress
                );
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

                let detail = "";


                if (objectName) {

                    detail +=
                        objectName;
                }


                if (total > 0) {

                    if (detail) {

                        detail += " · ";
                    }


                    detail +=
                        `${current} de ${total} pasos`;
                }


                detailText.innerText =
                    detail;
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


                setProgressTarget(
                    100
                );


                if (progressText) {

                    progressText.innerText =
                        "100% - Finalizado";
                }


                if (activityText) {

                    activityText.innerText =
                        "Documento generado correctamente.";
                }


                if (detailText) {

                    detailText.innerText =
                        `${total} de ${total} pasos`;
                }


                // =============================================
                // DOWNLOAD
                // =============================================

                setTimeout(
                    () => {

                        window.location.href =

                            `/api/ds140/download/${currentJobId}`;

                    },
                    650
                );


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


                showProgressError(
                    job.error ||
                    "Error generando documento"
                );

                showAppModal(
                    job.error ||
                    "Error generando documento"
                );


                resetButton();
            }

        }
        catch (error) {

            console.error(
                "[DS140 STATUS]",
                error
            );

            statusFailures += 1;

            // Fallo momentáneo: se sigue consultando.
            if (statusFailures < MAX_STATUS_FAILURES) {

                const activityText =
                    document.getElementById(
                        "activity-text"
                    );

                if (activityText) {

                    activityText.innerText =
                        `Reconectando con el servidor... ` +
                        `(intento ${statusFailures} de ${MAX_STATUS_FAILURES})`;
                }

                return;
            }


            if (statusInterval) {

                clearInterval(
                    statusInterval
                );

                statusInterval =
                    null;
            }

            const lost = /\((404|502|503)\)/.test(error.message);

            const message = lost
                ? "El servidor se reinició y el proceso se perdió " +
                  `(${error.message.match(/\((\d+)\)/)[1]}).`
                : error.message;

            showProgressError(
                message
            );

            showAppModal(
                message
            );


            resetButton();
        }
    }


    // =====================================================
    // RESET BUTTON
    // =====================================================

    function resetButton() {

        const button =
            document.querySelector(
                ".doc-action-ds140"
            );


        if (!button) {

            return;
        }


        button.disabled =
            false;


        button.classList.remove(
            "is-processing"
        );
    }

    // =====================================================
    // OBTENER DATOS DEL DIALOG
    // =====================================================

    function getRegisterFormData() {

        const requiresSchema =
            fileStore.sql.length > 0;

        return {

            autor:
                fieldOrUndefined("dialog_author"),

            nombre_desarrollo:
                fieldOrUndefined("dialog_development_name"),

            empresa:
                fieldOrUndefined("dialog_company"),

            esquema:
                requiresSchema
                    ? fieldOrUndefined("dialog_schema")
                    : (document.getElementById("dialog_schema")?.value.trim() || ""),

            numero_ticket:
                fieldOrUndefined("dialog_ticket"),

            requiresSchema:
                requiresSchema
        };
    }

    // =====================================================
    // REGISTRAR OBJETOS
    // =====================================================

    async function registerObjects() {

        const data =
            getRegisterFormData();


        // Campos vacíos: ya vienen como UNDEFINED.


        const totalFiles =

            fileStore.vb.length +
            fileStore.apex.length +
            fileStore.oic.length +
            fileStore.bip.length +
            fileStore.sql.length;


        if (totalFiles === 0) {

            showAppModal(
                "Debe seleccionar al menos un archivo."
            );

            return;
        }


        // =====================================================
        // RESPONSE CONTAINER
        // =====================================================

        const responseContainer =
            document.getElementById(
                "register-response"
            );


        if (responseContainer) {

            responseContainer.style.display =
                "block";

            responseContainer.innerHTML = `
            <strong>
                Procesando objetos...
            </strong>

            <br><br>

            Analizando ${totalFiles}
            archivo(s) y registrando
            objetos en la matriz.
        `;
        }


        // =====================================================
        // BUTTON
        // =====================================================

        const button =
            document.querySelector(
                ".dialog-primary-btn"
            );


        if (button) {

            button.disabled =
                true;

            button.innerText =
                "Registrando...";
        }


        try {

            // =================================================
            // FORMDATA
            // =================================================

            const formData =
                new FormData();


            formData.append(
                "empresa",
                data.empresa
            );


            formData.append(
                "numero_ticket",
                data.numero_ticket
            );


            formData.append(
                "objeto_pase",
                data.nombre_desarrollo
            );


            formData.append(
                "autor",
                data.autor
            );


            formData.append(
                "esquema",
                data.esquema
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
                "[MATRIZ] Enviando registro:",
                {
                    empresa:
                        data.empresa,

                    numero_ticket:
                        data.numero_ticket,

                    objeto_pase:
                        data.nombre_desarrollo,

                    esquema:
                        data.esquema,

                    archivos:
                        totalFiles
                }
            );


            // =================================================
            // FASTAPI
            // =================================================

            const response =
                await fetch(

                    "/api/matriz/register",

                    {
                        method:
                            "POST",

                        body:
                            formData
                    }
                );


            // =================================================
            // RESPONSE JSON
            // =================================================

            const responseText =
                await response.text();


            let result;


            try {

                result =
                    JSON.parse(
                        responseText
                    );

            }
            catch {

                result = {

                    status:
                        "ERROR",

                    mensaje:
                        responseText
                        ||
                        "El servidor no devolvió una respuesta válida."
                };
            }


            console.log(
                "[MATRIZ] Response:",
                result
            );


            // =================================================
            // RENDER RESULT
            // =================================================

            renderMatrixResponse(
                result,
                response.ok
            );

        }
        catch (error) {

            console.error(
                "[MATRIZ]",
                error
            );


            if (responseContainer) {

                responseContainer.innerHTML = `

                <div class="matrix-error-title">
                    Error registrando objetos
                </div>

                <div>
                    ${escapeHtml(
                    error.message
                )}
                </div>
            `;
            }

        }
        finally {

            if (button) {

                button.disabled =
                    false;

                button.innerText =
                    "Registrar Objetos";
            }
        }
    }

    // =====================================================
    // DESCARGAR MATRIZ
    // =====================================================

    async function downloadMatrix() {

        const ticket =
            document
                .getElementById(
                    "dialog_ticket"
                )
                ?.value
                .trim();


        if (!ticket) {

            showAppModal(
                "Debe ingresar el número de ticket."
            );

            return;
        }


        const button =
            document.querySelector(
                ".dialog-secondary-btn"
            );


        if (button) {

            button.disabled =
                true;

            button.innerText =
                "Generando PDF...";
        }


        try {

            console.log(
                "[MATRIZ PDF] Descargando ticket:",
                ticket
            );


            const response =
                await fetch(

                    `/api/matriz/download?ticket=${encodeURIComponent(
                        ticket
                    )
                    }`,

                    {
                        method:
                            "GET",

                        cache:
                            "no-store"
                    }
                );


            if (!response.ok) {

                const text =
                    await response.text();

                let message =
                    text;


                try {

                    const json =
                        JSON.parse(
                            text
                        );

                    message =
                        json.mensaje
                        ||
                        json.detail
                        ||
                        text;

                }
                catch {

                    // respuesta no JSON
                }


                throw new Error(
                    message
                );
            }


            // =================================================
            // PDF
            // =================================================

            const blob =
                await response.blob();


            const url =
                URL.createObjectURL(
                    blob
                );


            const link =
                document.createElement(
                    "a"
                );


            link.href =
                url;


            link.download =
                "NEO-GD-RG-03 Inventario de Objetos de Desarrollo.pdf";


            document.body.appendChild(
                link
            );


            link.click();


            link.remove();


            URL.revokeObjectURL(
                url
            );

        }
        catch (error) {

            console.error(
                "[MATRIZ PDF]",
                error
            );


            showAppModal(
                error.message
                ||
                "No fue posible descargar la matriz."
            );

        }
        finally {

            if (button) {

                button.disabled =
                    false;

                button.innerText =
                    "Descargar Matriz";
            }
        }
    }


    function openRegisterDialog() {

        console.log(
            "[MATRIZ] openRegisterDialog ejecutado"
        );

        const dialog =
            document.getElementById(
                "register-dialog"
            );

        console.log(
            "[MATRIZ] dialog encontrado:",
            dialog
        );

        const author =
            document.getElementById(
                "author_name"
            );

        const development =
            document.getElementById(
                "development_name"
            );

        const company =
            document.getElementById(
                "company_name"
            );

        const dialogAuthor =
            document.getElementById(
                "dialog_author"
            );

        const dialogCompany =
            document.getElementById(
                "dialog_company"
            );

        const dialogDevelopment =
            document.getElementById(
                "dialog_development_name"
            );

        const schemaGroup =
            document.getElementById(
                "schema-group"
            );

        const hasSchema =
            fileStore.sql.length > 0 ||
            fileStore.apex.length > 0;

        if (dialogAuthor) {
            dialogAuthor.value =
                author && author.value
                    ? author.value
                    : "";
        }

        if (dialogDevelopment) {
            dialogDevelopment.value =
                development && development.value
                    ? development.value
                    : "";
        }

        if (dialogCompany) {

            dialogCompany.value =
                company && company.value
                    ? company.value
                    : "";
        }

        if (schemaGroup) {
            schemaGroup.style.display =
                hasSchema
                    ? "block"
                    : "none";
        }

        if (dialog) {
            dialog.style.display =
                "flex";
        }
    }

    function closeRegisterDialog() {

        const dialog =
            document.getElementById(
                "register-dialog"
            );

        if (dialog) {
            dialog.style.display = "none";
        }
    }


    function renderMatrixResponse(
        result,
        httpOk
    ) {

        const container =
            document.getElementById(
                "register-response"
            );


        if (!container) {

            return;
        }


        container.style.display =
            "block";


        // =====================================================
        // ERROR GENERAL
        // =====================================================

        if (
            !httpOk ||
            result.status === "ERROR"
        ) {

            container.innerHTML = `

            <div class="matrix-error-title">
                Error procesando la matriz
            </div>

            <div>
                ${escapeHtml(
                result.mensaje
                ||
                result.detail
                ||
                "Se produjo un error."
            )}
            </div>
        `;

            return;
        }


        // =====================================================
        // SUMMARY
        // =====================================================

        const resumen =
            result.resumen
            ||
            {};


        const objetos =
            Array.isArray(
                result.objetos
            )
                ? result.objetos
                : [];


        const rows =
            objetos
                .map(
                    object => {

                        return `

                        <tr>

                            <td>
                                ${escapeHtml(
                            object.nombre_objeto
                            ||
                            object.id
                            ||
                            ""
                        )}
                            </td>

                            <td>
                                ${escapeHtml(
                            object.herramienta
                            ||
                            ""
                        )}
                            </td>

                            <td>
                                ${escapeHtml(
                            object.tipo
                            ||
                            "No Aplica"
                        )}
                            </td>

                            <td>
                                ${escapeHtml(
                            object.accion
                            ||
                            ""
                        )}
                            </td>

                            <td>
                                ${escapeHtml(
                            object.mensaje
                            ||
                            ""
                        )}
                            </td>

                        </tr>
                    `;
                    }
                )
                .join(
                    ""
                );


        container.innerHTML = `

        <div class="matrix-success-title">
            Registro procesado
        </div>

        <div class="matrix-owner">
            Owner:
            <strong>
                ${escapeHtml(
            result.owner
            ||
            ""
        )}
            </strong>
        </div>


        <div class="matrix-summary">

            <div>
                <strong>
                    ${resumen.recibidos || 0}
                </strong>
                <span>
                    Recibidos
                </span>
            </div>

            <div>
                <strong>
                    ${resumen.insertados || 0}
                </strong>
                <span>
                    Insertados
                </span>
            </div>

            <div>
                <strong>
                    ${resumen.actualizados || 0}
                </strong>
                <span>
                    Actualizados
                </span>
            </div>

            <div>
                <strong>
                    ${resumen.sin_cambios || 0}
                </strong>
                <span>
                    Sin cambios
                </span>
            </div>

            <div>
                <strong>
                    ${resumen.omitidos || 0}
                </strong>
                <span>
                    Omitidos
                </span>
            </div>

            <div>
                <strong>
                    ${resumen.errores || 0}
                </strong>
                <span>
                    Errores
                </span>
            </div>

        </div>


        <div class="matrix-result-table-wrapper">

            <table class="matrix-result-table">

                <thead>

                    <tr>

                        <th>
                            Objeto
                        </th>

                        <th>
                            Herramienta
                        </th>

                        <th>
                            Tipo
                        </th>

                        <th>
                            Acción
                        </th>

                        <th>
                            Mensaje
                        </th>

                    </tr>

                </thead>

                <tbody>
                    ${rows}
                </tbody>

            </table>

        </div>
    `;
    }


    // =====================================================
    // IM090 REQUIREMENTS
    // =====================================================

    let im090DatabasePrivileges = [];


    // =====================================================
    // ADD ROLE
    // =====================================================

    function addIM090Role(
        type,
        initialValue = ""
    ) {

        const container =
            document.getElementById(
                `im090_${type}_roles_container`
            );


        if (!container) {

            return;
        }


        const row =
            document.createElement(
                "div"
            );


        row.className =
            "im090-role-row";


        const input =
            document.createElement(
                "input"
            );


        input.type =
            "text";

        input.className =
            "im090-role-input";

        input.dataset.roleType =
            type;

        input.placeholder =
            "Ingrese el nombre del rol";

        input.value =
            initialValue;


        const removeButton =
            document.createElement(
                "button"
            );


        removeButton.type =
            "button";

        removeButton.className =
            "im090-remove-btn";

        removeButton.innerText =
            "×";


        removeButton.onclick =
            () => {

                row.remove();

            };


        row.appendChild(
            input
        );

        row.appendChild(
            removeButton
        );


        container.appendChild(
            row
        );
    }


    // =====================================================
    // ENSURE FIRST ROLE INPUT
    // =====================================================

    function ensureIM090RoleInput(
        type
    ) {

        const container =
            document.getElementById(
                `im090_${type}_roles_container`
            );


        if (
            container
            &&
            container.children.length === 0
        ) {

            addIM090Role(
                type
            );
        }
    }


    // =====================================================
    // DATABASE PRIVILEGES
    // =====================================================

    function addIM090DbPrivilege() {

        const input =
            document.getElementById(
                "im090_db_privilege_input"
            );


        if (!input) {

            return;
        }


        const value =
            input.value
                .trim()
                .toUpperCase();


        if (!value) {

            return;
        }


        const exists =
            im090DatabasePrivileges
                .some(
                    item =>
                        item.toUpperCase()
                        ===
                        value
                );


        if (!exists) {

            im090DatabasePrivileges.push(
                value
            );
        }


        input.value =
            "";


        renderIM090DbPrivileges();
    }


    // =====================================================
    // REMOVE DATABASE PRIVILEGE
    // =====================================================

    function removeIM090DbPrivilege(
        value
    ) {

        im090DatabasePrivileges =
            im090DatabasePrivileges.filter(
                item =>
                    item !== value
            );


        renderIM090DbPrivileges();
    }


    // =====================================================
    // RENDER DATABASE PRIVILEGES
    // =====================================================

    function renderIM090DbPrivileges() {

        const container =
            document.getElementById(
                "im090_db_privileges_list"
            );


        if (!container) {

            return;
        }


        container.innerHTML =
            "";


        im090DatabasePrivileges.forEach(
            privilege => {

                const chip =
                    document.createElement(
                        "div"
                    );


                chip.className =
                    "im090-db-chip";


                const text =
                    document.createElement(
                        "span"
                    );


                text.innerText =
                    privilege;


                const removeButton =
                    document.createElement(
                        "button"
                    );


                removeButton.type =
                    "button";

                removeButton.innerText =
                    "×";


                removeButton.onclick =
                    () => {

                        removeIM090DbPrivilege(
                            privilege
                        );
                    };


                chip.appendChild(
                    text
                );

                chip.appendChild(
                    removeButton
                );


                container.appendChild(
                    chip
                );
            }
        );
    }


    // =====================================================
    // IM090 - VISUAL BUILDER STUDIO BACKENDS
    // =====================================================
    //
    // Al abrir el diálogo se envían los zips de VB al
    // servidor, que devuelve los backends de cada extensión
    // (catalog.json). El usuario elige la autenticación de
    // cada uno y la selección viaja con el IM090.
    // =====================================================

    let im090VbAnalysis = [];

    let im090VbAuthMethods = [];

    let im090VbSignature = "";

    const im090VbAuthSelection = {};

    const IM090_VB_SERVER_KIND = {
        local: "servidor local",
        in_source: "servidor en el código fuente",
        reference: "apunta a otro backend"
    };


    function im090VbFilesSignature() {

        return fileStore.vb
            .map(file => `${file.name}:${file.size}:${file.lastModified}`)
            .join("|");
    }


    function im090VbKey(appIndex, backendId) {

        return `${appIndex}::${backendId}`;
    }


    async function loadIM090VbBackends() {

        const group =
            document.getElementById("im090_vb_backends_group");

        const container =
            document.getElementById("im090_vb_backends_container");

        if (!group || !container) {
            return;
        }

        if (fileStore.vb.length === 0) {

            group.style.display = "none";

            im090VbAnalysis = [];

            return;
        }

        group.style.display = "block";

        const signature = im090VbFilesSignature();

        if (
            signature === im090VbSignature
            &&
            im090VbAnalysis.length > 0
        ) {

            renderIM090VbBackends();

            return;
        }

        container.innerHTML =
            '<div class="im090-vb-note">Analizando aplicaciones...</div>';

        try {

            const formData = new FormData();

            fileStore.vb.forEach(
                file => formData.append("vb_files", file)
            );

            const response = await fetch(
                "/api/im090/vb-backends",
                {
                    method: "POST",
                    body: formData
                }
            );

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();

            im090VbAnalysis = data.apps || [];

            im090VbAuthMethods = data.auth_methods || [];

            im090VbSignature = signature;

            renderIM090VbBackends();
        }
        catch (error) {

            console.error("[IM090] backends VB:", error);

            container.innerHTML =
                '<div class="im090-vb-warning">'
                + "No se pudieron leer los backends de las aplicaciones: "
                + escapeHtml(error.message)
                + "</div>";
        }
    }


    function renderIM090VbBackends() {

        const container =
            document.getElementById("im090_vb_backends_container");

        if (!container) {
            return;
        }

        container.innerHTML = "";

        im090VbAnalysis.forEach((app, appIndex) => {

            const box = document.createElement("div");

            box.className = "im090-vb-app";

            const title = app.extension_name || app.file_name;

            const uiNames = (app.applications || [])
                .map(item => item.name)
                .join(", ");

            box.innerHTML =
                `<div class="im090-vb-app-title">${escapeHtml(title)}</div>`
                + '<div class="im090-vb-app-meta">'
                + escapeHtml(app.file_name)
                + (app.extension_id ? ` · ${escapeHtml(app.extension_id)}` : "")
                + (uiNames ? ` · App UI: ${escapeHtml(uiNames)}` : "")
                + "</div>";

            if (app.layout !== "extension") {

                box.insertAdjacentHTML(
                    "beforeend",
                    '<div class="im090-vb-note">'
                    + "No es una extensión de Visual Builder Studio "
                    + "(no tiene sources/services/self/catalog.json); "
                    + "no se configuran backends."
                    + "</div>"
                );

                container.appendChild(box);

                return;
            }

            if (!(app.backends || []).length) {

                box.insertAdjacentHTML(
                    "beforeend",
                    '<div class="im090-vb-note">La extensión no define backends propios.</div>'
                );
            }

            (app.backends || []).forEach(backend => {

                const row = document.createElement("div");

                row.className = "im090-vb-backend-row";

                const services = (backend.services || []).length;

                const details = [
                    backend.id,
                    IM090_VB_SERVER_KIND[backend.server_kind] || backend.server_kind,
                    services === 1 ? "1 servicio" : `${services} servicios`
                ];

                if (backend.reference) {
                    details.push(`→ ${backend.reference}`);
                }

                const name = document.createElement("div");

                name.className = "im090-vb-backend-name";

                name.innerHTML =
                    `<strong>${escapeHtml(backend.label)}</strong>`
                    + `<span class="im090-vb-backend-detail">${escapeHtml(details.join(" · "))}</span>`;

                const select = document.createElement("select");

                select.setAttribute(
                    "aria-label",
                    `Autenticación de ${backend.label}`
                );

                select.innerHTML =
                    '<option value="">Seleccione la autenticación...</option>'
                    + im090VbAuthMethods
                        .map(method =>
                            `<option value="${escapeHtml(method.key)}">${escapeHtml(method.label)}</option>`
                        )
                        .join("");

                const key = im090VbKey(appIndex, backend.id);

                select.value =
                    im090VbAuthSelection[key]
                    || backend.detected_auth
                    || "";

                if (select.value) {
                    im090VbAuthSelection[key] = select.value;
                }

                select.addEventListener("change", () => {
                    im090VbAuthSelection[key] = select.value;
                });

                row.appendChild(name);

                row.appendChild(select);

                box.appendChild(row);
            });

            if ((app.base_backends || []).length) {

                box.insertAdjacentHTML(
                    "beforeend",
                    '<div class="im090-vb-note">'
                    + "Backends de Oracle Cloud Applications (no requieren configuración): "
                    + escapeHtml(app.base_backends.join(", "))
                    + "</div>"
                );
            }

            (app.warnings || []).forEach(warning => {

                box.insertAdjacentHTML(
                    "beforeend",
                    `<div class="im090-vb-warning">${escapeHtml(warning)}</div>`
                );
            });

            container.appendChild(box);
        });
    }


    function collectIM090VbAuth() {

        // Lista alineada con fileStore.vb: [{file_name, selection}]
        return fileStore.vb.map((file, appIndex) => {

            const app = im090VbAnalysis[appIndex] || {};

            const selection = {};

            (app.backends || []).forEach(backend => {

                const value =
                    im090VbAuthSelection[im090VbKey(appIndex, backend.id)];

                if (value) {
                    selection[backend.id] = value;
                }
            });

            return {
                file_name: file.name,
                selection
            };
        });
    }


    function collectIM090VbSettings() {

        const value = id =>
            (document.getElementById(id)?.value || "").trim();

        return {
            source_env: value("im090_vb_source_env"),
            target_env: value("im090_vb_target_env"),
            target_erp_url: value("im090_vb_target_erp_url"),
            target_oic_url: value("im090_vb_target_oic_url"),
            repository: value("im090_vb_repository")
        };
    }


    function missingIM090VbAuth() {

        // Backends con servicios que aún no tienen autenticación
        const missing = [];

        im090VbAnalysis.forEach((app, appIndex) => {

            (app.backends || []).forEach(backend => {

                if (
                    (backend.services || []).length > 0
                    &&
                    !im090VbAuthSelection[im090VbKey(appIndex, backend.id)]
                ) {
                    missing.push(
                        `${backend.label} (${app.extension_name || app.file_name})`
                    );
                }
            });
        });

        return missing;
    }


    // =====================================================
    // OPEN IM090 DIALOG
    // =====================================================

    function openIM090Dialog() {

        const dialog =
            document.getElementById(
                "im090-dialog"
            );

        const requirementsTitle =
            document.getElementById(
                "im090_requirements_title"
            );


        if (requirementsTitle) {

            requirementsTitle.style.display =
                (
                    fileStore.bip.length > 0
                    ||
                    fileStore.oic.length > 0
                    ||
                    fileStore.sql.length > 0
                    ||
                    fileStore.vb.length > 0
                )
                    ?
                    "block"
                    :
                    "none";
        }

        // Backends de Visual Builder Studio (asíncrono)
        loadIM090VbBackends();

        // =================================================
        // ERP ROLE INPUT
        // =================================================

        if (fileStore.bip.length > 0) {

            ensureIM090RoleInput(
                "erp"
            );
        }


        // =================================================
        // OIC ROLES
        // =================================================

        const oicRolesGroup =
            document.getElementById(
                "im090_oic_roles_group"
            );


        if (oicRolesGroup) {

            oicRolesGroup.style.display =
                fileStore.oic.length > 0
                    ? "block"
                    : "none";
        }


        if (fileStore.oic.length > 0) {

            ensureIM090RoleInput(
                "oic"
            );
        }


        // =================================================
        // DATABASE PRIVILEGES
        // =================================================

        const dbPrivilegesGroup =
            document.getElementById(
                "im090_db_privileges_group"
            );


        if (dbPrivilegesGroup) {

            dbPrivilegesGroup.style.display =
                fileStore.sql.length > 0
                    ? "block"
                    : "none";
        }

        if (!dialog) {

            console.error(
                "[IM090] No existe el diálogo"
            );

            return;
        }


        // =================================================
        // PREFILL AUTHOR
        // =================================================

        const sourceAuthor =
            document.getElementById(
                "author_name"
            );


        const targetAuthor =
            document.getElementById(
                "im090_author"
            );


        if (targetAuthor) {

            targetAuthor.value =
                sourceAuthor
                    ? sourceAuthor.value
                    : "";
        }


        // =================================================
        // PREFILL DEVELOPMENT
        // =================================================

        const sourceDevelopment =
            document.getElementById(
                "development_name"
            );


        const targetDevelopment =
            document.getElementById(
                "im090_development_name"
            );


        if (targetDevelopment) {

            targetDevelopment.value =
                sourceDevelopment
                    ? sourceDevelopment.value
                    : "";
        }


        // =================================================
        // SQL -> SHOW SCHEMA
        // =================================================

        const schemaGroup =
            document.getElementById(
                "im090_schema_group"
            );


        if (schemaGroup) {

            schemaGroup.style.display =
                fileStore.sql.length > 0
                    ? "block"
                    : "none";
        }


        // =================================================
        // BIP -> SHOW ERP ROLES
        // =================================================

        const erpRolesGroup =
            document.getElementById(
                "im090_erp_roles_group"
            );


        if (erpRolesGroup) {

            erpRolesGroup.style.display =
                fileStore.bip.length > 0
                    ? "block"
                    : "none";
        }


        // =================================================
        // COMPONENT SUMMARY
        // =================================================

        const summary =
            document.getElementById(
                "im090_components_summary"
            );


        if (summary) {

            const components = [];


            if (fileStore.vb.length > 0) {

                components.push(
                    `Visual Builder (${fileStore.vb.length})`
                );
            }


            if (fileStore.apex.length > 0) {

                components.push(
                    `APEX (${fileStore.apex.length})`
                );
            }


            if (fileStore.oic.length > 0) {

                components.push(
                    `OIC (${fileStore.oic.length})`
                );
            }


            if (fileStore.bip.length > 0) {

                components.push(
                    `BI Publisher (${fileStore.bip.length})`
                );
            }


            if (fileStore.sql.length > 0) {

                components.push(
                    `Base de Datos (${fileStore.sql.length})`
                );
            }


            if (components.length > 0) {

                summary.innerHTML =
                    `
                    <strong>
                        Componentes detectados:
                    </strong>
                    <br>
                    ${components.join("<br>")}
                `;
            }
            else {

                summary.innerHTML =
                    `
                    <strong>
                        No hay componentes cargados.
                    </strong>
                `;
            }
        }


        dialog.style.display =
            "flex";
    }


    // =====================================================
    // CLOSE IM090 DIALOG
    // =====================================================

    function closeIM090Dialog() {

        const dialog =
            document.getElementById(
                "im090-dialog"
            );


        if (dialog) {

            dialog.style.display =
                "none";
        }
    }

    // =====================================================
    // IM090 JOB
    // =====================================================

    let currentIM090JobId =
        null;

    let im090StatusInterval =
        null;


    // =====================================================
    // GENERATE IM090
    // =====================================================

    async function generateIM090() {

        try {

            // =================================================
            // BASIC COMPONENT VALIDATION
            // =================================================

            const hasComponents = (

                fileStore.vb.length > 0
                ||
                fileStore.apex.length > 0
                ||
                fileStore.oic.length > 0
                ||
                fileStore.bip.length > 0
                ||
                fileStore.sql.length > 0

            );

            // =================================================
            // GENERATION TIME NOTICE
            // =================================================

            const durationNotice =
                document.getElementById(
                    "im090-duration-notice"
                );


            const durationNoticeText =
                document.getElementById(
                    "im090-duration-notice-text"
                );


            const hasOIC =
                fileStore.oic.length > 0;


            const hasVisualBuilder =
                fileStore.vb.length > 0;


            // =================================================
            // SHOW ONLY FOR HEAVY IM090 SECTIONS
            // =================================================

            if (durationNotice) {

                durationNotice.style.display =
                    (
                        hasOIC
                        ||
                        hasVisualBuilder
                    )
                        ?
                        "block"
                        :
                        "none";
            }


            // =================================================
            // MESSAGE
            // =================================================

            if (
                durationNoticeText
                &&
                (
                    hasOIC
                    ||
                    hasVisualBuilder
                )
            ) {

                if (
                    hasOIC
                    &&
                    hasVisualBuilder
                ) {

                    durationNoticeText.innerText =
                        (
                            "La generación del IM090 puede tardar "
                            +
                            "más de 10 minutos. El tiempo de procesamiento "
                            +
                            "depende de la cantidad de integraciones OIC "
                            +
                            "y puede incrementarse cuando el documento "
                            +
                            "incluye aplicaciones de Visual Builder."
                        );
                }

                else if (hasOIC) {

                    durationNoticeText.innerText =
                        (
                            "La generación del IM090 puede tardar "
                            +
                            "más de 10 minutos dependiendo de la cantidad "
                            +
                            "de integraciones OIC incluidas en el documento."
                        );
                }

                else {

                    durationNoticeText.innerText =
                        (
                            "La generación del IM090 puede requerir "
                            +
                            "varios minutos debido al procesamiento de "
                            +
                            "las aplicaciones de Visual Builder incluidas."
                        );
                }
            }


            if (!hasComponents) {

                showAppModal(
                    "Debe cargar al menos un componente."
                );

                return;
            }


            // =================================================
            // VISUAL BUILDER STUDIO - AUTENTICACIÓN
            // =================================================

            const missingVbAuth =
                missingIM090VbAuth();

            if (missingVbAuth.length > 0) {

                showAppModal(
                    "Seleccione la autenticación de los backends de "
                    + "Visual Builder Studio: "
                    + missingVbAuth.join(", ")
                    + "."
                );

                return;
            }


            // =================================================
            // VALUES
            // =================================================

            const author =
                fieldOrUndefined("im090_author");


            const developmentName =
                fieldOrUndefined("im090_development_name");


            const schemaName =
                fileStore.sql.length > 0
                    ? fieldOrUndefined("im090_schema")
                    : (document.getElementById("im090_schema")?.value.trim() || "");


            // Campos vacíos: ya vienen como UNDEFINED.


            // =================================================
            // BUTTON
            // =================================================

            const button =
                document.getElementById(
                    "im090_generate_btn"
                );


            if (button) {

                button.disabled =
                    true;

                button.innerText =
                    "Generando...";
            }


            // =================================================
            // FORMDATA
            // =================================================

            const formData =
                new FormData();


            formData.append(
                "author_name",
                author
            );


            formData.append(
                "development_name",
                developmentName
            );


            formData.append(
                "schema_name",
                schemaName
            );


            // =================================================
            // ERP ROLES
            // =================================================

            // =================================================
            // ERP ROLES
            // =================================================

            document
                .querySelectorAll(
                    '.im090-role-input[data-role-type="erp"]'
                )
                .forEach(
                    input => {

                        const value =
                            input.value.trim();


                        if (value) {

                            formData.append(
                                "erp_roles",
                                value
                            );
                        }
                    }
                );


            // =================================================
            // OIC ROLES
            // =================================================

            document
                .querySelectorAll(
                    '.im090-role-input[data-role-type="oic"]'
                )
                .forEach(
                    input => {

                        const value =
                            input.value.trim();


                        if (value) {

                            formData.append(
                                "oic_roles",
                                value
                            );
                        }
                    }
                );


            // =================================================
            // DATABASE PRIVILEGES
            // =================================================

            im090DatabasePrivileges.forEach(
                privilege => {

                    formData.append(
                        "database_privileges",
                        privilege
                    );
                }
            );



            // Autenticación elegida por backend de VB Studio
            if (fileStore.vb.length > 0) {

                formData.append(
                    "vb_backend_auth",
                    JSON.stringify(
                        collectIM090VbAuth()
                    )
                );

                formData.append(
                    "vb_install_settings",
                    JSON.stringify(
                        collectIM090VbSettings()
                    )
                );
            }


            // =================================================
            // EXISTING FILE STORE
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


            // =================================================
            // START
            // =================================================

            const response =
                await fetch(

                    "/api/im090/start",

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
                    `Error generando IM090 (${response.status}): ${errorText}`
                );
            }


            const result =
                await response.json();


            currentIM090JobId =
                result.job_id;


            // =================================================
            // CLOSE DIALOG
            // =================================================

            closeIM090Dialog();


            // =================================================
            // SHOW EXISTING PROGRESS BAR
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


            const activityText =
                document.getElementById(
                    "activity-text"
                );


            const detailText =
                document.getElementById(
                    "detail-text"
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
                    "0% - Preparando IM090";
            }


            if (activityText) {

                activityText.innerText =
                    "Analizando archivos y calculando pasos totales...";
            }


            if (detailText) {

                detailText.innerText =
                    "Preparando plan de generación...";
            }


            // =================================================
            // POLLING
            // =================================================

            if (im090StatusInterval) {

                clearInterval(
                    im090StatusInterval
                );
            }


            im090StatusInterval =
                setInterval(

                    checkIM090Status,

                    700
                );

        }
        catch (error) {

            console.error(
                "[IM090]",
                error
            );


            showAppModal(
                error.message
            );


            resetIM090Button();
        }
    }


    // =====================================================
    // CHECK IM090 STATUS
    // =====================================================

    async function checkIM090Status() {

        if (!currentIM090JobId) {

            return;
        }


        try {

            const response =
                await fetch(

                    `/api/im090/status/${currentIM090JobId}`,

                    {
                        cache:
                            "no-store"
                    }
                );


            if (!response.ok) {

                const errorText =
                    await response.text();


                throw new Error(
                    `Error consultando IM090 (${response.status}): ${errorText}`
                );
            }


            const job =
                await response.json();


            // =================================================
            // JOB DATA
            // =================================================

            const progress =
                Number(
                    job.progress || 0
                );


            const component =
                job.step || "IM090";


            const activity =
                job.activity || "";


            const objectName =
                job.object || "";


            const current =
                Number(
                    job.current || 0
                );


            const total =
                Number(
                    job.total || 0
                );


            // =================================================
            // UI
            // =================================================

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


            // =================================================
            // BAR
            // =================================================

            if (progressBar) {

                progressBar.style.width =
                    `${progress}%`;
            }


            // =================================================
            // MAIN STATUS
            //
            // Ejemplo:
            //
            // 42% - IM090 - OIC
            // =================================================

            if (progressText) {

                progressText.innerText =
                    `${progress}% - ${component}`;
            }


            // =================================================
            // CURRENT ACTIVITY
            //
            // Ejemplo:
            //
            // Panel de activación generado
            // =================================================

            if (activityText) {

                if (
                    total > 0
                    &&
                    current > 0
                ) {

                    activityText.innerText =
                        (
                            `Paso ${current} de ${total}: `
                            +
                            activity
                        );
                }

                else {

                    activityText.innerText =
                        activity
                        ||
                        "Analizando archivos y calculando pasos...";
                }
            }


            // =================================================
            // CURRENT OBJECT
            //
            // Ejemplo:
            //
            // NEO PE GRE UOM SYNC
            // 18 de 69 pasos completados
            // =================================================

            if (detailText) {

                let detailParts = [];


                if (objectName) {

                    detailParts.push(
                        objectName
                    );
                }


                if (total > 0) {

                    detailParts.push(
                        `${current} de ${total} pasos completados`
                    );
                }

                else {

                    detailParts.push(
                        "Preparando plan de generación..."
                    );
                }


                detailText.innerText =
                    detailParts.join(
                        " · "
                    );
            }


            // =================================================
            // COMPLETED
            // =================================================

            if (
                job.status ===
                "completed"
            ) {

                clearInterval(
                    im090StatusInterval
                );


                im090StatusInterval =
                    null;


                // =============================================
                // FORCE FINAL UI
                // =============================================

                if (progressBar) {

                    progressBar.style.width =
                        "100%";
                }


                if (progressText) {

                    progressText.innerText =
                        "100% - IM090 Finalizado";
                }


                if (activityText) {

                    activityText.innerText =
                        "Paquete de instalación generado correctamente.";
                }


                if (detailText) {

                    if (total > 0) {

                        detailText.innerText =
                            `${total} de ${total} pasos completados`;
                    }

                    else {

                        detailText.innerText =
                            "Proceso completado";
                    }
                }


                // =============================================
                // DOWNLOAD
                // =============================================

                setTimeout(
                    () => {

                        window.location.href =
                            `/api/im090/download/${currentIM090JobId}`;

                    },
                    500
                );


                resetIM090Button();


                return;
            }


            // =================================================
            // ERROR
            // =================================================

            if (
                job.status === "error"
                ||
                job.status === "failed"
            ) {

                clearInterval(
                    im090StatusInterval
                );


                im090StatusInterval =
                    null;


                showAppModal(
                    job.error
                    ||
                    "Error generando IM090."
                );


                resetIM090Button();
            }

        }

        catch (error) {

            console.error(
                "[IM090 STATUS]",
                error
            );


            if (im090StatusInterval) {

                clearInterval(
                    im090StatusInterval
                );


                im090StatusInterval =
                    null;
            }


            showAppModal(
                error.message
            );


            resetIM090Button();
        }
    }


    // =====================================================
    // RESET IM090 BUTTON
    // =====================================================

    function resetIM090Button() {

        const button =
            document.getElementById(
                "im090_generate_btn"
            );


        if (button) {

            button.disabled =
                false;

            button.innerText =
                "Generar IM090";
        }

        const durationNotice =
            document.getElementById(
                "im090-duration-notice"
            );


        if (durationNotice) {

            durationNotice.style.display =
                "none";
        }

    }

    // =====================================================
    // PUBLIC FUNCTIONS
    // =====================================================

    window.generateDS140 =
        generateDS140;


    window.generateDS140 =
        generateDS140;

    window.registerObjects =
        registerObjects;


    window.downloadMatrix =
        downloadMatrix;


    window.openRegisterDialog =
        openRegisterDialog;

    window.closeRegisterDialog =
        closeRegisterDialog;

    window.openIM090Dialog =
        openIM090Dialog;

    window.closeIM090Dialog =
        closeIM090Dialog;

    window.generateIM090 =
        generateIM090;

    window.addIM090Role =
        addIM090Role;


    window.addIM090DbPrivilege =
        addIM090DbPrivilege;

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