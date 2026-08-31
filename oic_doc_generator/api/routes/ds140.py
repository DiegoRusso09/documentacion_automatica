from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException
)

from fastapi.responses import (
    FileResponse
)

from io import BytesIO

import asyncio
import traceback

from oic_doc_generator.api.job_manager import (
    create_job,
    get_job,
    fail_job
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
# BACKGROUND WORKER
# =========================================================

def run_ds140_job(

    job_id,

    author_name,

    development_name,

    company_name,

    vb_files,

    apex_files,

    oic_files,

    bip_files,

    sql_files
):

    try:

        print(
            f"[DS140] Iniciando job {job_id}"
        )

        generate_ds140_service(

            job_id,

            author_name,

            development_name,

            company_name,

            vb_files,

            apex_files,

            oic_files,

            bip_files,

            sql_files
        )

        print(
            f"[DS140] Job {job_id} finalizado"
        )

    except Exception as error:

        print(
            "========================================"
        )

        print(
            f"[DS140 ERROR] Job: {job_id}"
        )

        print(
            f"[DS140 ERROR] {error}"
        )

        traceback.print_exc()

        print(
            "========================================"
        )

        fail_job(
            job_id,
            error
        )


# =========================================================
# START DS140
# =========================================================

@router.post("/ds140/start")
async def start_ds140(

    author_name: str = Form(...),

    development_name: str = Form(...),

    company_name: str = Form(...),

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

    print(
        f"[DS140] Job creado: {job_id}"
    )


    # =====================================================
    # COPY FILES WHILE REQUEST IS ACTIVE
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


    print(
        "[DS140] Archivos recibidos:",
        {
            "vb":
                len(vb_memory_files),

            "apex":
                len(apex_memory_files),

            "oic":
                len(oic_memory_files),

            "bip":
                len(bip_memory_files),

            "sql":
                len(sql_memory_files)
        }
    )


    # =====================================================
    # BACKGROUND PROCESS
    # =====================================================

    asyncio.create_task(

        asyncio.to_thread(

            run_ds140_job,

            job_id,

            author_name,

            development_name,

            company_name,

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

    job = get_job(
        job_id
    )


    if job is None:

        print(
            f"[DS140 STATUS] Job no encontrado: {job_id}"
        )

        raise HTTPException(

            status_code=404,

            detail=
                f"Job no encontrado: {job_id}"
        )


    return job


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

        raise HTTPException(

            status_code=404,

            detail="Job no encontrado"
        )


    if (
        job["status"]
        !=
        "completed"
    ):

        raise HTTPException(

            status_code=409,

            detail="Job todavía no completado"
        )


    return FileResponse(

        path=
            job["download"],

        filename=
            "entrega.zip",

        media_type=
            "application/zip"
    )