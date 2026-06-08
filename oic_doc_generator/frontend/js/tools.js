async function extractParContent() {

    const fileInput =
        document.getElementById(
            "par_file"
        );

    if (!fileInput.files.length) {

        alert(
            "Seleccione un archivo PAR"
        );

        return;
    }

    const formData =
        new FormData();

    formData.append(
        "file",
        fileInput.files[0]
    );

    const response =
        await fetch(
            "/api/tools/par",
            {
                method: "POST",
                body: formData
            }
        );

    const result =
        await response.json();

    document.getElementById(
        "tool-result"
    ).textContent =
        JSON.stringify(
            result,
            null,
            4
        );
}


async function extractIarContent() {

    const fileInput =
        document.getElementById(
            "iar_file"
        );

    if (!fileInput.files.length) {

        alert(
            "Seleccione un archivo IAR"
        );

        return;
    }

    const formData =
        new FormData();

    formData.append(
        "file",
        fileInput.files[0]
    );

    const response =
        await fetch(
            "/api/tools/iar",
            {
                method: "POST",
                body: formData
            }
        );

    const result =
        await response.json();

    document.getElementById(
        "tool-result"
    ).textContent =
        JSON.stringify(
            result,
            null,
            4
        );
}


async function extractOtbiContent() {

    const fileInput =
        document.getElementById(
            "otbi_file"
        );

    if (!fileInput.files.length) {

        alert(
            "Seleccione un archivo"
        );

        return;
    }

    const formData =
        new FormData();

    formData.append(
        "file",
        fileInput.files[0]
    );

    const response =
        await fetch(
            "/api/tools/otbi",
            {
                method: "POST",
                body: formData
            }
        );

    const result =
        await response.json();

    document.getElementById(
        "tool-result"
    ).textContent =
        JSON.stringify(
            result,
            null,
            4
        );
}