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

from oic_doc_generator.api.routes.matriz import (
    router as matriz_router
)

from pathlib import Path

from oic_doc_generator.api.routes.tools import (
    router as tools_router
)

from oic_doc_generator.api.routes.ds140 import (
    router as ds140_router
)

from oic_doc_generator.api.routes.ai import (
    router as ai_router
)

from oic_doc_generator.api.routes.im090 import (
    router as im090_router
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

app.include_router(
    im090_router,
    prefix="/api"
)

app.include_router(

    tools_router,

    prefix="/api"
)

app.include_router(
    matriz_router,
    prefix="/api"
)

app.include_router(
    ai_router,
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

@app.get("/api/graphviz")
def graphviz_debug():

    import shutil

    return {
        "dot": shutil.which("dot")
    }

@app.get("/api/playwright-debug")
def playwright_debug():

    import os

    paths = []

    for root, dirs, files in os.walk("/opt/render"):

        for file in files:

            if (
                "chrome" in file.lower()
                or "chromium" in file.lower()
            ):

                paths.append(
                    os.path.join(root, file)
                )

    return {
        "found": paths
    }

@app.get("/api/playwright-check")
def playwright_check():

    import os

    path = (
        "/opt/render/.cache/ms-playwright/"
        "chromium-1223/chrome-linux64/chrome"
    )

    return {

        "exists":
            os.path.exists(path),

        "is_file":
            os.path.isfile(path),

        "path":
            path
    }

@app.get("/api/debug-vb")
def debug_vb():

    import inspect

    from oic_doc_generator.backend.renderers.screenshot_renderer import (
        render_html_to_image
    )

    return {
        "file": inspect.getfile(
            render_html_to_image
        )
    }

@app.get("/api/deploy-info")
def deploy_info():

    import os
    import hashlib

    ds140_path = (
        FRONTEND_DIR
        / "pages"
        / "ds140.html"
    )

    router_path = (
        FRONTEND_DIR
        / "js"
        / "router.js"
    )

    ds140_js_path = (
        FRONTEND_DIR
        / "js"
        / "ds140.js"
    )

    result = {

        "render_git_commit":
            os.environ.get(
                "RENDER_GIT_COMMIT",
                "NO_DISPONIBLE"
            ),

        "frontend_dir":
            str(
                FRONTEND_DIR
            ),

        "ds140_path":
            str(
                ds140_path
            ),

        "ds140_exists":
            ds140_path.exists(),

        "router_exists":
            router_path.exists(),

        "ds140_js_exists":
            ds140_js_path.exists()
    }

    if ds140_path.exists():

        content = ds140_path.read_text(
            encoding="utf-8"
        )

        result[
            "ds140_sha256"
        ] = hashlib.sha256(
            content.encode(
                "utf-8"
            )
        ).hexdigest()

        result[
            "ds140_contains_oic"
        ] = (
            "Oracle Integration Cloud"
            in content
        )

        result[
            "ds140_contains_oic_dropzone"
        ] = (
            "oic_dropzone"
            in content
        )

        oic_position = content.find(
            "Oracle Integration Cloud"
        )

        if oic_position >= 0:

            start = max(
                0,
                oic_position - 500
            )

            end = min(
                len(content),
                oic_position + 2500
            )

            result[
                "oic_html"
            ] = content[
                start:end
            ]

        else:

            result[
                "oic_html"
            ] = "NO ENCONTRADO"

    return result