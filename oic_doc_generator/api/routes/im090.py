# =========================================================
# FILE:
# oic_doc_generator/api/routes/im090.py
# =========================================================

from io import BytesIO
from typing import List, Optional
import os


from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    Form,
    UploadFile
)

from fastapi.responses import (
    FileResponse,
    JSONResponse
)


from oic_doc_generator.api.services.im090_service import (
    generate_im090_service
)

from oic_doc_generator.api.job_manager import (
    create_job,
    get_job,
    fail_job,
    initialize_progress
)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter()


# =========================================================
# UPLOADFILE -> MEMORY FILE
# =========================================================
#
# IMPORTANTE:
#
# Los UploadFile no deben enviarse directamente al
# BackgroundTask.
#
# Primero copiamos el contenido a memoria para garantizar
# que siga disponible cuando la petición HTTP ya terminó.
#
# =========================================================

async def to_memory_files(
    uploaded_files: Optional[List[UploadFile]]
):

    result = []


    if not uploaded_files:

        return result


    for uploaded_file in uploaded_files:

        content = (
            await uploaded_file.read()
        )


        memory_file = BytesIO(
            content
        )


        memory_file.name = (
            uploaded_file.filename
            or
            "archivo"
        )


        memory_file.seek(
            0
        )


        result.append(
            memory_file
        )


    return result


# =========================================================
# RUN IM090 JOB
# =========================================================

def run_im090_job(

    job_id,

    author_name,

    development_name,

    schema_name,

    vb_files,

    apex_files,

    oic_files,

    bip_files,

    sql_files,

    erp_roles,

    approvers

):

    try:

        # =================================================
        # PROGRESS
        # =================================================
        #
        # Con BD:
        #
        # 1. Procesamiento BD
        # 2. Generación Word
        # 3. ZIP
        #
        # Sin BD:
        #
        # 1. Generación Word
        # 2. ZIP
        #
        # =================================================

        total_points = (
            3
            if sql_files
            else 2
        )


        initialize_progress(
            job_id,
            total_points
        )


        generate_im090_service(

            job_id=
                job_id,

            author_name=
                author_name,

            development_name=
                development_name,

            schema_name=
                schema_name,

            vb_files=
                vb_files,

            apex_files=
                apex_files,

            oic_files=
                oic_files,

            bip_files=
                bip_files,

            sql_files=
                sql_files,

            erp_roles=
                erp_roles,

            reviewers=
                [],

            approvers=
                approvers
        )


    except Exception as error:

        print(
            "[IM090] ERROR:",
            repr(error)
        )


        fail_job(
            job_id,
            error
        )


# =========================================================
# START IM090
# =========================================================

@router.post(
    "/im090/start"
)
async def start_im090(

    background_tasks: BackgroundTasks,

    author_name: str = Form(...),

    development_name: str = Form(...),

    schema_name: str = Form(""),

    erp_roles: Optional[List[str]] = Form(None),

    approvers: Optional[List[str]] = Form(None),

    vb_files: Optional[List[UploadFile]] = File(None),

    apex_files: Optional[List[UploadFile]] = File(None),

    oic_files: Optional[List[UploadFile]] = File(None),

    bip_files: Optional[List[UploadFile]] = File(None),

    sql_files: Optional[List[UploadFile]] = File(None)

):

    # =====================================================
    # NORMALIZE TEXT
    # =====================================================

    author_name = (
        author_name
        or
        ""
    ).strip()


    development_name = (
        development_name
        or
        ""
    ).strip()


    schema_name = (
        schema_name
        or
        ""
    ).strip()


    # =====================================================
    # BASIC VALIDATION
    # =====================================================

    if not author_name:

        return JSONResponse(

            status_code=400,

            content={
                "status":
                    "ERROR",

                "message":
                    "Debe indicar el autor del documento."
            }
        )


    if not development_name:

        return JSONResponse(

            status_code=400,

            content={
                "status":
                    "ERROR",

                "message":
                    "Debe indicar el nombre del desarrollo."
            }
        )


    # =====================================================
    # COPY FILES TO MEMORY
    # =====================================================

    vb_memory = await to_memory_files(
        vb_files
    )

    apex_memory = await to_memory_files(
        apex_files
    )

    oic_memory = await to_memory_files(
        oic_files
    )

    bip_memory = await to_memory_files(
        bip_files
    )

    sql_memory = await to_memory_files(
        sql_files
    )


    # =====================================================
    # DATABASE SCHEMA VALIDATION
    # =====================================================

    if (
        sql_memory
        and
        not schema_name
    ):

        return JSONResponse(
            status_code=400,
            content={
                "status": "ERROR",
                "message":
                    (
                        "Debe indicar el esquema de "
                        "Base de Datos cuando existen "
                        "objetos SQL."
                    )
            }
        )

    # =====================================================
    # AT LEAST ONE COMPONENT
    # =====================================================

    if not any([

        vb_memory,
        apex_memory,
        oic_memory,
        bip_memory,
        sql_memory

    ]):

        return JSONResponse(
            status_code=400,
            content={
                "status": "ERROR",
                "message":
                    "Debe cargar al menos un componente "
                    "para generar el IM090."
            }
        )


    # =====================================================
    # CREATE JOB
    # =====================================================

    job_id = (
        create_job()
    )


    # =====================================================
    # START BACKGROUND PROCESS
    # =====================================================

    background_tasks.add_task(

        run_im090_job,

        job_id,

        author_name,

        development_name,

        schema_name,

        vb_memory,

        apex_memory,

        oic_memory,

        bip_memory,

        sql_memory,

        erp_roles or [],

        approvers or []
    )

    # =====================================================
    # RESPONSE
    # =====================================================

    return {

        "status":
            "started",

        "job_id":
            job_id
    }


# =========================================================
# STATUS
# =========================================================

@router.get(
    "/im090/status/{job_id}"
)
async def get_im090_status(
    job_id: str
):

    job = (
        get_job(
            job_id
        )
    )


    if not job:

        return JSONResponse(

            status_code=404,

            content={
                "status":
                    "ERROR",

                "message":
                    (
                        f"Job no encontrado: "
                        f"{job_id}"
                    )
            }
        )


    return job


# =========================================================
# DOWNLOAD
# =========================================================

@router.get(
    "/im090/download/{job_id}"
)
async def download_im090(
    job_id: str
):

    job = (
        get_job(
            job_id
        )
    )


    if not job:

        return JSONResponse(

            status_code=404,

            content={
                "status":
                    "ERROR",

                "message":
                    (
                        f"Job no encontrado: "
                        f"{job_id}"
                    )
            }
        )


    # =====================================================
    # NOT FINISHED
    # =====================================================

    if (
        job.get(
            "status"
        )
        !=
        "completed"
    ):

        return JSONResponse(

            status_code=409,

            content={
                "status":
                    "ERROR",

                "message":
                    "El IM090 todavía no ha finalizado."
            }
        )


    # =====================================================
    # DOWNLOAD PATH
    # =====================================================

    download_path = (
        job.get(
            "download"
        )
    )


    if (
        not download_path
        or
        not os.path.exists(
            download_path
        )
    ):

        return JSONResponse(

            status_code=404,

            content={
                "status":
                    "ERROR",

                "message":
                    (
                        "No se encontró el paquete "
                        "IM090 generado."
                    )
            }
        )


    # =====================================================
    # FILE
    # =====================================================

    return FileResponse(

        path=
            download_path,

        media_type=
            "application/zip",

        filename=
            "IM090_entrega.zip"
    )