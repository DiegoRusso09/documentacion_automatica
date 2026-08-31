# =========================================================
# FILE:
# oic_doc_generator/api/routes/ai.py
# =========================================================

from fastapi import APIRouter

from fastapi.responses import (
    JSONResponse
)

from pydantic import BaseModel


from oic_doc_generator.api.services.ai_text_service import (
    naturalize_technical_text
)


router = APIRouter()


# =========================================================
# REQUEST
# =========================================================

class NaturalizeTextRequest(
    BaseModel
):

    text: str


# =========================================================
# POST /ai/naturalize
# =========================================================

@router.post(
    "/ai/naturalize"
)
async def naturalize_text(
    request: NaturalizeTextRequest
):

    try:

        natural_text = (
            naturalize_technical_text(
                request.text
            )
        )


        return {

            "status":
                "OK",

            "original_text":
                request.text,

            "natural_text":
                natural_text
        }


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
            "[AI TEXT] ERROR:",
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