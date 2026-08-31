// =========================================================
// FILE:
// static/js/tools.js
// =========================================================


// =========================================================
// EXPLORE FILE
// =========================================================

async function exploreOracleArchive(
    fileInputId
) {

    const fileInput =
        document.getElementById(
            fileInputId
        );


    if (
        !fileInput ||
        !fileInput.files ||
        !fileInput.files.length
    ) {

        alert(
            "Seleccione un archivo."
        );

        return;
    }


    const file =
        fileInput.files[0];


    const resultContainer =
        document.getElementById(
            "tool-result"
        );


    if (!resultContainer) {

        console.error(
            "[TOOLS] No existe #tool-result"
        );

        return;
    }


    // =====================================================
    // LOADING
    // =====================================================

    resultContainer.innerHTML = "";


    const loading =
        document.createElement(
            "div"
        );


    loading.className =
        "tools-loading";


    loading.textContent =
        `Analizando ${file.name}...`;


    resultContainer.appendChild(
        loading
    );


    // =====================================================
    // REQUEST
    // =====================================================

    const formData =
        new FormData();


    formData.append(
        "file",
        file
    );


    try {

        const response =
            await fetch(
                "/api/tools/explore",
                {
                    method:
                        "POST",

                    body:
                        formData
                }
            );


        let result;


        try {

            result =
                await response.json();

        }
        catch {

            throw new Error(
                "El servidor devolvió una respuesta inválida."
            );
        }


        if (!response.ok) {

            throw new Error(
                result.mensaje ||
                "No fue posible analizar el archivo."
            );
        }


        console.log(
            "[TOOLS] Resultado:",
            result
        );


        // =================================================
        // RENDER RESULT
        // =================================================

        renderArchiveExplorer(
            result
        );

    }
    catch (error) {

        console.error(
            "[TOOLS] ERROR:",
            error
        );


        resultContainer.innerHTML = "";


        const errorBox =
            document.createElement(
                "div"
            );


        errorBox.className =
            "tools-error";


        errorBox.textContent =
            error.message ||
            "Ocurrió un error procesando el archivo.";


        resultContainer.appendChild(
            errorBox
        );
    }
}


// =========================================================
// BUTTON WRAPPERS
// =========================================================

async function extractParContent() {

    await exploreOracleArchive(
        "par_file"
    );
}


async function extractIarContent() {

    await exploreOracleArchive(
        "iar_file"
    );
}


async function extractOtbiContent() {

    await exploreOracleArchive(
        "otbi_file"
    );
}


// =========================================================
// FORMAT BYTES
// =========================================================

function formatBytes(
    bytes
) {

    if (
        bytes === null ||
        bytes === undefined
    ) {

        return "";
    }


    if (bytes === 0) {

        return "0 B";
    }


    const units = [
        "B",
        "KB",
        "MB",
        "GB"
    ];


    const index =
        Math.floor(
            Math.log(bytes) /
            Math.log(1024)
        );


    const value =
        bytes /
        Math.pow(
            1024,
            index
        );


    return (
        value.toFixed(
            index === 0
                ? 0
                : 2
        )
        +
        " "
        +
        units[
            Math.min(
                index,
                units.length - 1
            )
        ]
    );
}


// =========================================================
// FILE ICON
// =========================================================

function getFileIcon(
    item
) {

    if (
        item.type ===
        "folder"
    ) {

        return "📁";
    }


    const extension = (
        item.extension ||
        ""
    ).toLowerCase();


    const icons = {

        ".xml":
            "📄",

        ".xsl":
            "📄",

        ".xslt":
            "📄",

        ".xsd":
            "📄",

        ".wsdl":
            "📄",

        ".jca":
            "⚙️",

        ".json":
            "📋",

        ".properties":
            "⚙️",

        ".sql":
            "🗄️",

        ".iar":
            "📦",

        ".par":
            "📦",

        ".xdoz":
            "📊",

        ".xdmz":
            "🧩",

        ".xdrz":
            "📦",

        ".zip":
            "📦",

        ".jar":
            "📦",

        ".png":
            "🖼️",

        ".jpg":
            "🖼️",

        ".jpeg":
            "🖼️"
    };


    return (
        icons[
            extension
        ]
        ||
        "📄"
    );
}


// =========================================================
// BUILD DOWNLOAD URL
// =========================================================

function buildDownloadUrl(
    sessionId,
    path
) {

    const params =
        new URLSearchParams();


    params.set(
        "session_id",
        sessionId
    );


    params.set(
        "path",
        path
    );


    return (
        "/api/tools/download?"
        +
        params.toString()
    );
}


// =========================================================
// CREATE FILE NODE
// =========================================================

function createFileNode(
    item,
    sessionId
) {

    const row =
        document.createElement(
            "div"
        );


    row.className =
        "archive-file-row";


    // =====================================================
    // LEFT
    // =====================================================

    const info =
        document.createElement(
            "div"
        );


    info.className =
        "archive-file-info";


    const icon =
        document.createElement(
            "span"
        );


    icon.className =
        "archive-icon";


    icon.textContent =
        getFileIcon(
            item
        );


    const name =
        document.createElement(
            "span"
        );


    name.className =
        "archive-file-name";


    name.textContent =
        item.name;


    info.appendChild(
        icon
    );


    info.appendChild(
        name
    );


    // =====================================================
    // RIGHT
    // =====================================================

    const actions =
        document.createElement(
            "div"
        );


    actions.className =
        "archive-file-actions";


    if (
        item.size !==
        undefined
    ) {

        const size =
            document.createElement(
                "span"
            );


        size.className =
            "archive-file-size";


        size.textContent =
            formatBytes(
                item.size
            );


        actions.appendChild(
            size
        );
    }


    const download =
        document.createElement(
            "a"
        );


    download.className =
        "archive-download";


    download.textContent =
        "Descargar";


    download.href =
        buildDownloadUrl(
            sessionId,
            item.path
        );


    download.setAttribute(
        "download",
        item.name
    );


    actions.appendChild(
        download
    );


    row.appendChild(
        info
    );


    row.appendChild(
        actions
    );


    return row;
}


// =========================================================
// CREATE FOLDER NODE
// =========================================================

function createFolderNode(
    item,
    sessionId,
    level = 0
) {

    const details =
        document.createElement(
            "details"
        );


    details.className =
        "archive-folder";


    // Root levels abiertos inicialmente
    if (level === 0) {

        details.open =
            true;
    }


    const summary =
        document.createElement(
            "summary"
        );


    summary.className =
        "archive-folder-summary";


    const icon =
        document.createElement(
            "span"
        );


    icon.className =
        "archive-icon";


    icon.textContent =
        "📁";


    const name =
        document.createElement(
            "span"
        );


    name.className =
        "archive-folder-name";


    name.textContent =
        item.name;


    const count =
        document.createElement(
            "span"
        );


    count.className =
        "archive-folder-count";


    count.textContent =
        `(${(item.children || []).length})`;


    summary.appendChild(
        icon
    );


    summary.appendChild(
        name
    );


    summary.appendChild(
        count
    );


    details.appendChild(
        summary
    );


    // =====================================================
    // CHILDREN
    // =====================================================

    const children =
        document.createElement(
            "div"
        );


    children.className =
        "archive-folder-children";


    for (
        const child
        of
        item.children || []
    ) {

        if (
            child.type ===
            "folder"
        ) {

            children.appendChild(

                createFolderNode(
                    child,
                    sessionId,
                    level + 1
                )
            );

        }
        else {

            children.appendChild(

                createFileNode(
                    child,
                    sessionId
                )
            );
        }
    }


    details.appendChild(
        children
    );


    return details;
}


// =========================================================
// RENDER ARCHIVE EXPLORER
// =========================================================

function renderArchiveExplorer(
    result
) {

    const container =
        document.getElementById(
            "tool-result"
        );


    if (!container) {

        return;
    }


    container.innerHTML =
        "";


    // =====================================================
    // HEADER
    // =====================================================

    const header =
        document.createElement(
            "div"
        );


    header.className =
        "archive-result-header";


    const title =
        document.createElement(
            "div"
        );


    title.className =
        "archive-result-title";


    title.textContent =
        result.file_name ||
        "Archivo";


    const badge =
        document.createElement(
            "span"
        );


    badge.className =
        "archive-type-badge";


    badge.textContent =
        result.archive_type ||
        "ARCHIVE";


    title.appendChild(
        badge
    );


    const summary =
        document.createElement(
            "div"
        );


    summary.className =
        "archive-result-summary";


    summary.textContent =
        `${result.folders_count || 0} carpetas · `
        +
        `${result.files_count || 0} archivos · `
        +
        "Sesión disponible por 30 minutos";


    header.appendChild(
        title
    );


    header.appendChild(
        summary
    );


    container.appendChild(
        header
    );


    // =====================================================
    // TREE
    // =====================================================

    const treeContainer =
        document.createElement(
            "div"
        );


    treeContainer.className =
        "archive-tree";


    const tree =
        result.tree ||
        [];


    if (!tree.length) {

        const empty =
            document.createElement(
                "div"
            );


        empty.className =
            "archive-empty";


        empty.textContent =
            "El archivo no contiene elementos para mostrar.";


        treeContainer.appendChild(
            empty
        );

    }
    else {

        for (
            const item
            of
            tree
        ) {

            if (
                item.type ===
                "folder"
            ) {

                treeContainer.appendChild(

                    createFolderNode(
                        item,
                        result.session_id,
                        0
                    )
                );

            }
            else {

                treeContainer.appendChild(

                    createFileNode(
                        item,
                        result.session_id
                    )
                );
            }
        }
    }


    container.appendChild(
        treeContainer
    );
}


// =========================================================
// GLOBAL FUNCTIONS
// =========================================================

window.extractParContent =
    extractParContent;

window.extractIarContent =
    extractIarContent;

window.extractOtbiContent =
    extractOtbiContent;