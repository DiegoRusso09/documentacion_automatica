from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form
)

from fastapi.responses import (
    FileResponse
)

from io import BytesIO

import asyncio

from oic_doc_generator.api.job_manager import (
    create_job,
    get_job
)

from oic_doc_generator.api.services.ds140_service import (
    generate_ds140_service
)

router = APIRouter()


@router.post("/ds140/start")
async def start_ds140(

    author_name: str = Form(...),

    development_name: str = Form(...),

    files: list[UploadFile] = File(...)
):

    job_id = create_job()

    memory_files = []

    for file in files:

        content = await file.read()

        stream = BytesIO(
            content
        )

        stream.name = (
            file.filename
        )

        memory_files.append(
            stream
        )

    asyncio.create_task(

        asyncio.to_thread(

            generate_ds140_service,

            job_id,

            author_name,

            development_name,

            memory_files
        )
    )

    return {

        "job_id": job_id
    }


@router.get("/ds140/status/{job_id}")
def get_status(
    job_id: str
):

    return get_job(
        job_id
    )


@router.get("/ds140/download/{job_id}")
def download_file(
    job_id: str
):

    job = get_job(
        job_id
    )

    if not job:

        return {
            "error": "job not found"
        }

    if job["status"] != "completed":

        return {
            "error": "job not completed"
        }

    return FileResponse(

        path=job["download"],

        filename="entrega.zip",

        media_type="application/zip"
    )