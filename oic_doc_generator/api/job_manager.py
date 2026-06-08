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

        "object": "",

        "current": 0,

        "total": 0,

        "download": None,

        "error": None,

        "total_points": 0,

        "completed_points": 0
    }

    return job_id


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

def initialize_progress(
    job_id,
    total_points
):

    job = jobs.get(job_id)

    if not job:
        return

    job["total_points"] = total_points

    job["completed_points"] = 0

    job["current"] = 0

    job["total"] = total_points

def advance_progress(
    job_id,
    component,
    detail,
    object_name="",
    points=1
):

    job = jobs.get(
        job_id
    )

    if not job:

        return

    job["completed_points"] += points

    completed = job["completed_points"]

    total = max(
        job["total_points"],
        1
    )

    progress = int(
        (
            completed
            /
            total
        )
        * 100
    )

    if progress > 100:

        progress = 100

    job["progress"] = progress

    job["step"] = component

    job["activity"] = detail

    job["object"] = object_name

    job["current"] = completed

    job["total"] = total