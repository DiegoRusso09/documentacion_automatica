let currentJobId = null;

let statusInterval = null;


async function generateDS140() {

    try {

        const button =
            document.querySelector(
                ".generate-btn"
            );

        button.disabled = true;

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

        const inputs = [

            "vb_files",

            "apex_files",

            "oic_files",

            "bip_files",

            "sql_files"
        ];

        for (const inputId of inputs) {

            const input =
                document.getElementById(
                    inputId
                );

            if (!input) {
                continue;
            }

            for (const file of input.files) {

                formData.append(
                    "files",
                    file
                );
            }
        }

        const response =
            await fetch(

                "/api/ds140/start",

                {
                    method: "POST",
                    body: formData
                }
            );

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

        alert(
            error.message
        );

        resetButton();
    }
}


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

    progressBar.style.width =
        `${job.progress}%`;

    progressText.innerText =
        `${job.progress}% - ${job.step}`;

    activityText.innerText =
        job.activity || "";

    if (

        job.current > 0

        &&

        job.total > 0

    ) {

        detailText.innerText =

            `${job.current} de ${job.total}`;

    }

    else {

        detailText.innerText = "";
    }

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


function resetButton() {

    const button =
        document.querySelector(
            ".generate-btn"
        );

    button.disabled = false;

    button.innerText =
        "Generar Documento DS140";
}