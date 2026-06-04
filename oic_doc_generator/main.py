from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware
)

from fastapi.staticfiles import (
    StaticFiles
)

from fastapi.responses import (
    FileResponse
)

from pathlib import Path

from oic_doc_generator.api.routes.ds140 import (
    router as ds140_router
)

app = FastAPI()

# =========================================================
# CORS
# =========================================================

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

# =========================================================
# FRONTEND
# =========================================================

project_root = (

    Path(__file__)
    .resolve()
    .parent
    .parent
)

frontend_path = (

    project_root
    / "frontend"
)

app.mount(

    "/static",

    StaticFiles(

        directory=str(
            frontend_path
        )
    ),

    name="static"
)

# =========================================================
# ROUTES
# =========================================================

app.include_router(

    ds140_router,

    prefix="/api"
)

# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return FileResponse(

        frontend_path
        / "index.html"
    )

# =========================================================
# HEALTH
# =========================================================

@app.get("/api/health")
def health():

    return {

        "status": "ok"
    }