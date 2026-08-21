import uuid
import json
import os
import tempfile


# =========================================================
# JOB STORAGE
# =========================================================

JOBS_DIR = os.path.join(
    tempfile.gettempdir(),
    "ds140_jobs"
)


os.makedirs(
    JOBS_DIR,
    exist_ok=True
)


# =========================================================
# JOB PATH
# =========================================================

def _get_job_path(
    job_id
):

    return os.path.join(
        JOBS_DIR,
        f"{job_id}.json"
    )


# =========================================================
# SAVE JOB
# =========================================================

def _save_job(
    job_id,
    job
):

    job_path = _get_job_path(
        job_id
    )


    # =====================================================
    # ATOMIC WRITE
    # =====================================================
    #
    # Primero escribimos un archivo temporal y después
    # reemplazamos el definitivo.
    #
    # Así /status nunca leerá un JSON a medio escribir.
    # =====================================================

    temp_path = (
        job_path
        +
        ".tmp"
    )


    with open(
        temp_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            job,
            file,
            ensure_ascii=False,
            indent=2
        )


    os.replace(
        temp_path,
        job_path
    )


# =========================================================
# CREATE JOB
# =========================================================

def create_job():

    job_id = str(
        uuid.uuid4()
    )


    job = {

        "status":
            "running",

        "progress":
            0,

        "step":
            "Iniciando",

        "activity":
            "",

        "object":
            "",

        "current":
            0,

        "total":
            0,

        "download":
            None,

        "error":
            None,

        "total_points":
            0,

        "completed_points":
            0
    }


    _save_job(
        job_id,
        job
    )


    print(
        f"[JOB] Creado: {job_id}"
    )


    return job_id


# =========================================================
# GET JOB
# =========================================================

def get_job(
    job_id
):

    job_path = _get_job_path(
        job_id
    )


    if not os.path.exists(
        job_path
    ):

        print(
            f"[JOB] No encontrado: {job_id}"
        )

        return None


    try:

        with open(
            job_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(
                file
            )

    except Exception as error:

        print(
            f"[JOB] Error leyendo {job_id}: {error}"
        )

        return None


# =========================================================
# UPDATE ACTIVITY
# =========================================================

def update_activity(
    job_id,
    activity,
    current=0,
    total=0
):

    job = get_job(
        job_id
    )


    if not job:

        return


    job["activity"] = (
        activity
    )


    job["current"] = (
        current
    )


    job["total"] = (
        total
    )


    _save_job(
        job_id,
        job
    )


# =========================================================
# COMPLETE JOB
# =========================================================

def complete_job(
    job_id,
    download_path
):

    job = get_job(
        job_id
    )


    if not job:

        return


    job["status"] = (
        "completed"
    )


    job["progress"] = (
        100
    )


    job["step"] = (
        "Finalizado"
    )


    job["download"] = (
        download_path
    )


    _save_job(
        job_id,
        job
    )


# =========================================================
# FAIL JOB
# =========================================================

def fail_job(
    job_id,
    error
):

    job = get_job(
        job_id
    )


    if not job:

        return


    job["status"] = (
        "error"
    )


    job["error"] = (
        str(
            error
        )
    )


    _save_job(
        job_id,
        job
    )


# =========================================================
# INITIALIZE PROGRESS
# =========================================================

def initialize_progress(
    job_id,
    total_points
):

    job = get_job(
        job_id
    )


    if not job:

        return


    job["total_points"] = (
        total_points
    )


    job["completed_points"] = (
        0
    )


    job["current"] = (
        0
    )


    job["total"] = (
        total_points
    )


    _save_job(
        job_id,
        job
    )


# =========================================================
# ADVANCE PROGRESS
# =========================================================

def advance_progress(
    job_id,
    component,
    detail,
    object_name="",
    points=1
):

    job = get_job(
        job_id
    )


    if not job:

        return


    job["completed_points"] += (
        points
    )


    completed = (
        job[
            "completed_points"
        ]
    )


    total = max(

        job[
            "total_points"
        ],

        1
    )


    progress = int(

        (
            completed
            /
            total
        )
        *
        100
    )


    if progress > 100:

        progress = (
            100
        )


    job["progress"] = (
        progress
    )


    job["step"] = (
        component
    )


    job["activity"] = (
        detail
    )


    job["object"] = (
        object_name
    )


    job["current"] = (
        completed
    )


    job["total"] = (
        total
    )


    _save_job(
        job_id,
        job
    )