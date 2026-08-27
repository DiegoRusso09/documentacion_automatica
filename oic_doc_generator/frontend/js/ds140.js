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
        catch (error) {

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

                const errorText =
                    await response.text();

                throw new Error(
                    `Error consultando estado (${response.status}): ${errorText}`
                );
            }


            const job =
                await response.json();


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
        catch (error) {

            console.error(
                "[DS140 STATUS]",
                error
            );


            if (statusInterval) {

                clearInterval(
                    statusInterval
                );

                statusInterval =
                    null;
            }


            alert(
                error.message
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
    // OBTENER DATOS DEL DIALOG
    // =====================================================

    function getRegisterFormData() {

        const requiresSchema =
            fileStore.sql.length > 0;

        return {

            autor:
                document
                    .getElementById(
                        "dialog_author"
                    )
                    ?.value
                    .trim()
                || "",

            nombre_desarrollo:
                document
                    .getElementById(
                        "dialog_development_name"
                    )
                    ?.value
                    .trim()
                || "",

            empresa:
                document
                    .getElementById(
                        "dialog_company"
                    )
                    ?.value
                    .trim()
                || "",

            esquema:
                document
                    .getElementById(
                        "dialog_schema"
                    )
                    ?.value
                    .trim()
                || "",

            numero_ticket:
                document
                    .getElementById(
                        "dialog_ticket"
                    )
                    ?.value
                    .trim()
                || "",

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


        // =====================================================
        // VALIDATIONS
        // =====================================================

        if (!data.autor) {

            alert(
                "Debe ingresar el autor."
            );

            return;
        }


        if (!data.nombre_desarrollo) {

            alert(
                "Debe ingresar el nombre de desarrollo."
            );

            return;
        }


        if (!data.empresa) {

            alert(
                "Debe ingresar la empresa."
            );

            return;
        }


        if (
            data.requiresSchema &&
            !data.esquema
        ) {

            alert(
                "Debe ingresar el esquema."
            );

            return;
        }


        if (!data.numero_ticket) {

            alert(
                "Debe ingresar el número de ticket."
            );

            return;
        }


        const totalFiles =

            fileStore.vb.length +
            fileStore.apex.length +
            fileStore.oic.length +
            fileStore.bip.length +
            fileStore.sql.length;


        if (totalFiles === 0) {

            alert(
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

            alert(
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


            alert(
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

        const dialogAuthor =
            document.getElementById(
                "dialog_author"
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