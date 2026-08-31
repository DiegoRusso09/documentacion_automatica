# =========================================================
# FILE:
# oic_doc_generator/api/routes/tools.py
# =========================================================

import mimetypes
import os


from fastapi import (
    APIRouter,
    File,
    Query,
    UploadFile
)


from fastapi.responses import (
    FileResponse,
    JSONResponse
)


from oic_doc_generator.api.services.tools_service import (
    explore_archive_service,
    download_archive_file_service
)


router = APIRouter()


# =========================================================
# EXPLORE ARCHIVE
# =========================================================

@router.post(
    "/tools/explore"
)
async def tools_explore(
    file: UploadFile = File(...)
):

    try:

        result = (
            explore_archive_service(
                uploaded_file=
                    file.file,

                original_name=
                    file.filename
            )
        )


        return JSONResponse(
            status_code=200,
            content=result
        )


    except ValueError as error:

        return JSONResponse(
            status_code=400,
            content={
                "status":
                    "ERROR",

                "mensaje":
                    str(
                        error
                    )
            }
        )


    except Exception as error:

        print(
            "[TOOLS] ERROR:",
            repr(
                error
            )
        )


        return JSONResponse(
            status_code=500,
            content={
                "status":
                    "ERROR",

                "mensaje":
                    str(
                        error
                    )
            }
        )


# =========================================================
# DOWNLOAD INTERNAL FILE
# =========================================================

@router.get(
    "/tools/download"
)
async def tools_download(

    session_id: str = Query(...),

    path: str = Query(...)
):

    try:

        file_path = (
            download_archive_file_service(
                session_id=
                    session_id,

                file_path=
                    path
            )
        )


        file_name = os.path.basename(
            file_path
        )


        media_type = (
            mimetypes.guess_type(
                file_name
            )[0]
            or
            "application/octet-stream"
        )


        return FileResponse(

            path=
                file_path,

            filename=
                file_name,

            media_type=
                media_type
        )


    except FileNotFoundError as error:

        return JSONResponse(
            status_code=404,
            content={
                "status":
                    "ERROR",

                "mensaje":
                    str(
                        error
                    )
            }
        )


    except ValueError as error:

        return JSONResponse(
            status_code=400,
            content={
                "status":
                    "ERROR",

                "mensaje":
                    str(
                        error
                    )
            }
        )


    except Exception as error:

        print(
            "[TOOLS DOWNLOAD] ERROR:",
            repr(
                error
            )
        )


        return JSONResponse(
            status_code=500,
            content={
                "status":
                    "ERROR",

                "mensaje":
                    str(
                        error
                    )
            }
        )