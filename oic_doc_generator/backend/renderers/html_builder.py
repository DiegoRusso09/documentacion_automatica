# =========================================================
# FILE:
# oic_doc_generator/renderers/html_builder.py
# =========================================================

import os
import re

from pathlib import Path

from bs4 import BeautifulSoup

from oic_doc_generator.backend.utils.oj_translator import (
    translate_oj_html
)


# =========================================================
# LOAD VB BASE CSS
# =========================================================

def load_vb_base_css():

    current_dir = Path(
        __file__
    ).resolve().parent

    project_root = (
        current_dir.parent.parent
    )

    css_path = (
        project_root
        / "templates"
        / "vb_base.css"
    )

    if not css_path.exists():

        print(
            "[HTML_BUILDER] vb_base.css no encontrado"
        )

        return ""

    with open(

        css_path,

        "r",

        encoding="utf-8"
    ) as file:

        css = file.read()

    print(
        "[HTML_BUILDER] vb_base.css cargado"
    )

    return css


# =========================================================
# FIX IMAGE PATHS
# =========================================================

def normalize_image_paths(
    html
):

    if not html:

        return ""

    # =====================================================
    # :src="[[ $application.path + 'resources/images/x.png' ]]"
    # =====================================================

    html = re.sub(

        r':src="\[\[\s*\$application\.path\s*\+\s*[\'"]([^\'"]+)[\'"]\s*\]\]"',

        r'src="\1"',

        html
    )

    # =====================================================
    # src="[[ $application.path + 'resources/images/x.png' ]]"
    # =====================================================

    html = re.sub(

        r'src="\[\[\s*\$application\.path\s*\+\s*[\'"]([^\'"]+)[\'"]\s*\]\]"',

        r'src="\1"',

        html
    )

    return html


# =========================================================
# EXTRACT FOOTER
# =========================================================

def extract_footer(
    shell_html
):

    soup = BeautifulSoup(
        shell_html,
        "html.parser"
    )

    footer_html = ""

    footer = soup.find(
        "footer"
    )

    if footer:

        footer_html = str(
            footer
        )

        footer.extract()

    remaining_html = str(
        soup
    )

    return (

        remaining_html,

        footer_html
    )


# =========================================================
# CLEAN HTML
# =========================================================

def clean_html(
    html
):

    if not html:

        return ""

    replacements = [

        "oj-module",

        "oj-defer"
    ]

    for item in replacements:

        html = html.replace(
            f"</{item}>",
            ""
        )

    return html


# =========================================================
# BUILD CSS
# =========================================================

def build_combined_css(
    app_css
):

    vb_base_css = load_vb_base_css()

    final_css = f"""

    {vb_base_css}

    {app_css}

    """

    return final_css


# =========================================================
# BUILD BODY STRUCTURE
# =========================================================

def build_body_structure(
    header_html,
    body_html,
    footer_html
):

    final_body = f"""
    <div id="vb-shell">

        <header id="vb-header">

            {header_html}

        </header>

        <main id="vb-main-content">

            {body_html}

        </main>

        <footer id="vb-footer">

            {footer_html}

        </footer>

    </div>
    """

    return final_body


# =========================================================
# BUILD COMPLETE HTML
# =========================================================

def build_complete_html(
    shell_html,
    page_html,
    app_css
):

    # =====================================================
    # CLEAN
    # =====================================================

    shell_html = clean_html(
        shell_html
    )

    page_html = clean_html(
        page_html
    )

    # =====================================================
    # FIX IMAGE PATHS
    # =====================================================

    shell_html = normalize_image_paths(
        shell_html
    )

    page_html = normalize_image_paths(
        page_html
    )

    # =====================================================
    # SPLIT HEADER / FOOTER
    # =====================================================

    header_html, footer_html = extract_footer(
        shell_html
    )

    # =====================================================
    # TRANSLATE OJ
    # =====================================================

    header_html = translate_oj_html(
        header_html
    )

    body_html = translate_oj_html(
        page_html
    )

    footer_html = translate_oj_html(
        footer_html
    )

    # =====================================================
    # CSS
    # =====================================================

    final_css = build_combined_css(
        app_css
    )

    # =====================================================
    # BODY
    # =====================================================

    body_structure = build_body_structure(

        header_html=
            header_html,

        body_html=
            body_html,

        footer_html=
            footer_html
    )

    # =====================================================
    # FINAL HTML
    # =====================================================

    final_html = f"""
    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <style>

        * {{
            box-sizing:border-box;
        }}

        html {{
            width:100%;
            
        }}

        body {{
            margin:0;
            padding:0;
            width:100%;
            background:#ffffff;
            font-family:Arial, Helvetica, sans-serif;
            overflow-x:hidden;
        }}

        #vb-shell {{
            width:100%;
            display:flex;
            flex-direction:column;
        }}

        #vb-header {{
            width:100%;
            flex-shrink:0;
        }}

        #vb-main-content {{
            width:100%;
            padding:16px;
            box-sizing:border-box;
        }}

        #vb-footer {{
            width:100%;
            flex-shrink:0;
        }}

        img {{
            max-width:100%;
            display:inline-block;
        }}

        table {{
            width:100%;
            border-collapse:collapse;
        }}

        input,
        textarea,
        select,
        button {{
            font-family:Arial;
        }}

        .oj-flex {{
            display:flex;
            flex-wrap:wrap;
            gap:16px;
            width:100%;
            align-items:flex-start;
        }}

        {final_css}

        </style>

    </head>

    <body>

        {body_structure}

    </body>

    </html>
    """

    print(
        "[HTML_BUILDER] HTML final construido"
    )

    return final_html