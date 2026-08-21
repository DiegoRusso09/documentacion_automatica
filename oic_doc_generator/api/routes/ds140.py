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


# =========================================================
# CONVERT UPLOADFILES TO MEMORY FILES
# =========================================================

async def to_memory_files(
    uploaded_files
):

    memory_files = []

    for uploaded_file in uploaded_files:

        content = await uploaded_file.read()

        stream = BytesIO(
            content
        )

        stream.name = (
            uploaded_file.filename
        )

        memory_files.append(
            stream
        )

    return memory_files


# =========================================================
# START DS140
# =========================================================

@router.post("/ds140/start")
async def start_ds140(

    author_name: str = Form(...),

    development_name: str = Form(...),

    vb_files: list[UploadFile] = File(
        default=[]
    ),

    apex_files: list[UploadFile] = File(
        default=[]
    ),

    oic_files: list[UploadFile] = File(
        default=[]
    ),

    bip_files: list[UploadFile] = File(
        default=[]
    ),

    sql_files: list[UploadFile] = File(
        default=[]
    )
):

    job_id = create_job()


    # =====================================================
    # COPY FILES WHILE REQUEST IS STILL ACTIVE
    # =====================================================

    vb_memory_files = (
        await to_memory_files(
            vb_files
        )
    )

    apex_memory_files = (
        await to_memory_files(
            apex_files
        )
    )

    oic_memory_files = (
        await to_memory_files(
            oic_files
        )
    )

    bip_memory_files = (
        await to_memory_files(
            bip_files
        )
    )

    sql_memory_files = (
        await to_memory_files(
            sql_files
        )
    )


    # =====================================================
    # BACKGROUND PROCESS
    # =====================================================

    asyncio.create_task(

        asyncio.to_thread(

            generate_ds140_service,

            job_id,

            author_name,

            development_name,

            vb_memory_files,

            apex_memory_files,

            oic_memory_files,

            bip_memory_files,

            sql_memory_files
        )
    )


    return {

        "job_id":
            job_id
    }


# =========================================================
# STATUS
# =========================================================

@router.get("/ds140/status/{job_id}")
def get_status(
    job_id: str
):

    return get_job(
        job_id
    )


# =========================================================
# DOWNLOAD
# =========================================================

@router.get("/ds140/download/{job_id}")
def download_file(
    job_id: str
):

    job = get_job(
        job_id
    )


    if not job:

        return {

            "error":
                "job not found"
        }


    if (
        job["status"]
        !=
        "completed"
    ):

        return {

            "error":
                "job not completed"
        }


    return FileResponse(

        path=
            job["download"],

        filename=
            "entrega.zip",

        media_type=
            "application/zip"
    )