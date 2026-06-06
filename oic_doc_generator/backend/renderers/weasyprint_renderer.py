from weasyprint import HTML
from pdf2image import convert_from_path

import os
import tempfile
import shutil


# =========================================================
# RENDER HTML TO IMAGE
# =========================================================

def render_html_to_image(
    html_content,
    resources_path=None
):

    temp_dir = tempfile.mkdtemp(
        prefix="vb_render_"
    )

    try:

        print("[WEASY] inicio")

        # =================================================
        # COPY RESOURCES
        # =================================================

        if resources_path:

            target_resources = os.path.join(
                temp_dir,
                "resources"
            )

            shutil.copytree(

                resources_path,

                target_resources,

                dirs_exist_ok=True
            )

        # =================================================
        # FILES
        # =================================================

        html_file = os.path.join(
            temp_dir,
            "page.html"
        )

        pdf_file = os.path.join(
            temp_dir,
            "page.pdf"
        )

        png_file = os.path.join(
            temp_dir,
            "page.png"
        )

        # =================================================
        # SAVE HTML
        # =================================================

        with open(

            html_file,

            "w",

            encoding="utf-8"

        ) as f:

            f.write(
                html_content
            )

        print(
            "[WEASY] html guardado"
        )

        print(
            "[WEASY] html size =",
            len(html_content)
        )

        print(
            "[WEASY] html path =",
            html_file
        )

        # =================================================
        # GENERATE PDF
        # =================================================

        print(
            "[WEASY] generando pdf"
        )

        HTML(
            filename=html_file,
            base_url=temp_dir
        ).write_pdf(
            pdf_file
        )

        print(
            "[WEASY] pdf generado"
        )

        # =================================================
        # PDF -> PNG
        # =================================================

        print(
            "[WEASY] convirtiendo png"
        )

        pages = convert_from_path(

            pdf_file,

            dpi=200
        )

        if not pages:

            raise Exception(
                "No se generó ninguna página PDF"
            )

        pages[0].save(

            png_file,

            "PNG"
        )

        print(
            "[WEASY] png generado"
        )

        return png_file

    except Exception as e:

        print(
            "[WEASY] ERROR:",
            str(e)
        )

        raise Exception(
            f"WeasyPrint Error: {str(e)}"
        )