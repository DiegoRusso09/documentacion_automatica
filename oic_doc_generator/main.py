from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware
)

from oic_doc_generator.api.routes.ds140 import (
    router as ds140_router
)

app = FastAPI()

app.add_middleware(

    CORSMiddleware,

    allow_origins=[
        "*"
    ],

    allow_credentials=True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ]
)

app.include_router(

    ds140_router,

    prefix="/api"
)

@app.get("/api/health")
def health():

    return {
        "status": "ok"
    }