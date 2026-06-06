from weasyprint import HTML
from pdf2image import convert_from_path

import os
import tempfile
import shutil


def render_html_to_image(
    html_content,
    resources_path=None
):
    
    temp_dir = tempfile.mkdtemp()

    try:

        if resources_path:
            print("[WEASY] inicio")
            target_resources = os.path.join(
                temp_dir,
                "resources"
            )

            shutil.copytree(
                resources_path,
                target_resources,
                dirs_exist_ok=True
            )

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

        print("[WEASY] html guardado")

        with open(
            html_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                html_content
            )

        print("[WEASY] generando pdf")

        HTML(
            filename=html_file
        ).write_pdf(
            pdf_file
        )

        print("[WEASY] convirtiendo png")
        
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
        
        print("[WEASY] png generado")

        return png_file

    except Exception as e:

        raise Exception(
            f"WeasyPrint Error: {str(e)}"
        )