# =========================================================
# FILE:
# oic_doc_generator/renderers/screenshot_renderer.py
# =========================================================

import os
import shutil
import subprocess
import sys
import tempfile
import threading

from playwright.sync_api import (
    sync_playwright
)


# =========================================================
# CREATE TEMP DIRECTORY
# =========================================================

def create_temp_render_directory():

    temp_dir = tempfile.mkdtemp(
        prefix="vb_render_"
    )

    print(
        f"[SCREENSHOT_RENDERER] temp dir: {temp_dir}"
    )

    return temp_dir


# =========================================================
# COPY RESOURCES
# =========================================================

def copy_resources_folder(
    resources_path,
    temp_dir
):

    if not resources_path:

        print(
            "[SCREENSHOT_RENDERER] resources_path vacío"
        )

        return

    if not os.path.exists(
        resources_path
    ):

        print(
            "[SCREENSHOT_RENDERER] resources no existe"
        )

        return

    target_resources = os.path.join(
        temp_dir,
        "resources"
    )

    try:

        shutil.copytree(

            resources_path,

            target_resources,

            dirs_exist_ok=True
        )

        print(
            f"[SCREENSHOT_RENDERER] resources copiado: {target_resources}"
        )

    except Exception as e:

        print(
            f"[SCREENSHOT_RENDERER] error copiando resources: {e}"
        )


# =========================================================
# SAVE HTML FILE
# =========================================================

def save_render_html(
    html_content,
    temp_dir
):

    html_path = os.path.join(
        temp_dir,
        "render.html"
    )

    with open(

        html_path,

        "w",

        encoding="utf-8"
    ) as file:

        file.write(
            html_content
        )

    print(
        f"[SCREENSHOT_RENDERER] HTML guardado: {html_path}"
    )

    return html_path


# =========================================================
# GENERATE SCREENSHOT
# =========================================================
#
# Opciones de Chromium para servidores con poca memoria
# (Render free: 512 MB para todo): sin GPU, sin extensiones,
# sin tareas en segundo plano y un solo proceso de render.
# No cambian cómo se ve la captura.
# =========================================================

_install_lock = threading.Lock()


def _install_chromium():

    # Descarga el navegador de Playwright si no está (p. ej. en
    # Render sin "playwright install chromium" en el build).
    with _install_lock:

        print("[PLAYWRIGHT] Chromium no instalado: descargando...")

        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True,
            timeout=600
        )

        print("[PLAYWRIGHT] Chromium instalado")


def launch_chromium(playwright):

    # Lanza Chromium con opciones de poca memoria. Si falta el
    # ejecutable, lo instala una vez y reintenta.
    try:

        return playwright.chromium.launch(
            headless=True,
            args=CHROMIUM_LOW_MEMORY_ARGS
        )

    except Exception as error:

        if "Executable doesn't exist" not in str(error):
            raise

        _install_chromium()

        return playwright.chromium.launch(
            headless=True,
            args=CHROMIUM_LOW_MEMORY_ARGS
        )


CHROMIUM_LOW_MEMORY_ARGS = [
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--disable-extensions",
    "--disable-background-networking",
    "--disable-default-apps",
    "--disable-sync",
    "--no-first-run",
    "--mute-audio",
    "--renderer-process-limit=1",
    "--single-process",
    "--no-zygote",
    "--js-flags=--max-old-space-size=256"
]

def generate_screenshot(
    html_path,
    output_png
):
    print("[PLAYWRIGHT] launch")
    with sync_playwright() as playwright:

        print(
            "PLAYWRIGHT EXECUTABLE:",
            playwright.chromium.executable_path
        )

        browser = launch_chromium(playwright)

        print("[PLAYWRIGHT] browser started")

        page = browser.new_page(

            viewport={

                "width": 1600,

                "height": 50
            }
        )

        # =================================================
        # LOAD FILE
        # =================================================
        
        print("[PLAYWRIGHT] goto")
        page.goto(

            f"file:///{html_path}",

            wait_until="networkidle"
        )
        print("[PLAYWRIGHT] page loaded")

        # =================================================
        # WAIT RENDER
        # =================================================

        page.wait_for_timeout(
            500
        )

        # =================================================
        # DEBUG LOG
        # =================================================

        print(
            "[SCREENSHOT_RENDERER] página renderizada"
        )

        # =================================================
        # SCREENSHOT
        # =================================================
        
        print("[PLAYWRIGHT] screenshot")
        page.screenshot(

            path=output_png,

            full_page=True
        )

        browser.close()

    print(
        f"[SCREENSHOT_RENDERER] screenshot generado: {output_png}"
    )

    return output_png


# =========================================================
# RENDER HTML TO IMAGE
# =========================================================

def render_html_to_image(
    html_content,
    resources_path
):

    # =====================================================
    # TEMP DIR
    # =====================================================

    temp_dir = create_temp_render_directory()

    # =====================================================
    # COPY RESOURCES
    # =====================================================

    copy_resources_folder(

        resources_path=
            resources_path,

        temp_dir=
            temp_dir
    )

    # =====================================================
    # SAVE HTML
    # =====================================================

    html_path = save_render_html(

        html_content=
            html_content,

        temp_dir=
            temp_dir
    )

    # =====================================================
    # OUTPUT IMAGE
    # =====================================================

    output_png = os.path.join(
        temp_dir,
        "output.png"
    )

    # =====================================================
    # GENERATE
    # =====================================================

    generate_screenshot(

        html_path=
            html_path,

        output_png=
            output_png
    )

    return output_png