from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File

from oic_doc_generator.api.services.tools_service import (
    extract_par_service,
    extract_iar_service,
    extract_otbi_service
)

router = APIRouter()


@router.post("/tools/par")
async def tools_par(
    file: UploadFile = File(...)
):

    return extract_par_service(
        file.file
    )


@router.post("/tools/iar")
async def tools_iar(
    file: UploadFile = File(...)
):

    return extract_iar_service(
        file.file
    )


@router.post("/tools/otbi")
async def tools_otbi(
    file: UploadFile = File(...)
):

    return extract_otbi_service(
        file.file
    )