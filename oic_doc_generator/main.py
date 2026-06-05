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

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)

# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

FRONTEND_DIR = BASE_DIR / "frontend"

# =========================================================
# STATIC
# =========================================================

app.mount(

    "/static",

    StaticFiles(
        directory=str(FRONTEND_DIR)
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

        FRONTEND_DIR / "index.html"
    )

# =========================================================
# HEALTH
# =========================================================

@app.get("/api/health")
def health():

    return {
        "status": "ok"
    }

@app.get("/api/debug")
def debug():

    return {

        "base_dir":
            str(BASE_DIR),

        "frontend_dir":
            str(FRONTEND_DIR),

        "frontend_exists":
            FRONTEND_DIR.exists(),

        "css_exists":
            (
                FRONTEND_DIR
                / "css"
                / "style.css"
            ).exists()
    }

@app.get("/api/mmdc")
def mmdc():

    import shutil

    return {

        "mmdc":
            shutil.which(
                "mmdc"
            )
    }

@app.get("/api/browser")
def browser():

    import shutil

    return {

        "chromium":
            shutil.which(
                "chromium"
            ),

        "google_chrome":
            shutil.which(
                "google-chrome"
            ),

        "mmdc":
            shutil.which(
                "mmdc"
            )
    }

@app.get("/api/playwright")
def playwright_path():

    import os

    result = []

    for root, dirs, files in os.walk(
        "/opt/render/.cache"
    ):
        for file in files:

            if (
                "chrome" in file.lower()
                or "chromium" in file.lower()
            ):
                result.append(
                    os.path.join(
                        root,
                        file
                    )
                )

    return result