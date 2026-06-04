import uuid

jobs = {}


def create_job():

    job_id = str(
        uuid.uuid4()
    )

    jobs[job_id] = {

        "status": "running",

        "progress": 0,

        "step": "Iniciando",

        "activity": "",

        "current": 0,

        "total": 0,

        "download": None,

        "error": None,

        "steps": [],

        "current_step": 0
    }

    return job_id


def configure_steps(
    job_id,
    steps
):

    jobs[job_id]["steps"] = steps

    jobs[job_id]["current_step"] = 0


def advance_step(
    job_id,
    description
):

    job = jobs.get(
        job_id
    )

    if not job:

        return

    total_steps = len(
        job["steps"]
    )

    if total_steps == 0:

        return

    job["current_step"] += 1

    progress = int(

        (
            job["current_step"]
            /
            total_steps
        )
        *
        100
    )

    job["progress"] = progress

    job["step"] = description

    job["activity"] = ""


def update_activity(
    job_id,
    activity,
    current=0,
    total=0
):

    job = jobs.get(
        job_id
    )

    if not job:

        return

    job["activity"] = activity

    job["current"] = current

    job["total"] = total


def complete_job(
    job_id,
    download_path
):

    jobs[job_id]["status"] = "completed"

    jobs[job_id]["progress"] = 100

    jobs[job_id]["step"] = "Finalizado"

    jobs[job_id]["download"] = download_path


def fail_job(
    job_id,
    error
):

    jobs[job_id]["status"] = "error"

    jobs[job_id]["error"] = str(error)


def get_job(
    job_id
):

    return jobs.get(
        job_id
    )