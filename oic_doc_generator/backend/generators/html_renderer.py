# =========================================================
# FILE:
# oic_doc_generator/generators/html_renderer.py
# =========================================================

import tempfile
import os
import shutil
import re

from pathlib import Path

from bs4 import BeautifulSoup

from playwright.sync_api import (
    sync_playwright
)

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
        current_dir.parent
    )

    css_path = (
        project_root
        / "templates"
        / "vb_base.css"
    )

    if not css_path.exists():

        return ""

    with open(

        css_path,

        "r",

        encoding="utf-8"
    ) as file:

        return file.read()


# =========================================================
# CLEAN HTML
# =========================================================

def clean_html(html):

    if not html:

        return ""

    replacements = [

        "oj-bind-text",

        "oj-bind-if",

        "oj-bind-for-each",

        "oj-module"
    ]

    for item in replacements:

        html = html.replace(
            f"</{item}>",
            ""
        )

    return html


# =========================================================
# SPLIT SHELL
# =========================================================

def split_shell(shell_html):

    shell_soup = BeautifulSoup(
        shell_html,
        "html.parser"
    )

    footer_html = ""

    footer = shell_soup.find(
        "footer"
    )

    if footer:

        footer_html = str(
            footer
        )

        footer.extract()

    header_html = str(
        shell_soup
    )

    return (

        header_html,

        footer_html
    )


# =========================================================
# COPY RESOURCES
# =========================================================

def copy_resources(
    temp_dir,
    base_path
):

    if not base_path:

        return

    source_resources = os.path.join(
        base_path,
        "resources"
    )

    if not os.path.exists(
        source_resources
    ):

        print(
            "[HTML_RENDERER] resources not found"
        )

        return

    target_resources = os.path.join(
        temp_dir,
        "resources"
    )

    try:

        shutil.copytree(

            source_resources,

            target_resources,

            dirs_exist_ok=True
        )

        print(
            f"[HTML_RENDERER] resources copied to: {target_resources}"
        )

    except Exception as e:

        print(
            f"[HTML_RENDERER] error copying resources: {e}"
        )


# =========================================================
# FIX IMAGE PATHS
# =========================================================

def fix_image_paths(html):

    if not html:

        return ""

    # =====================================================
    # :src
    # =====================================================

    html = re.sub(

        r':src="\[\[\s*\$application\.path\s*\+\s*[\'"]([^\'"]+)[\'"]\s*\]\]"',

        r'src="\1"',

        html
    )

    # =====================================================
    # src
    # =====================================================

    html = re.sub(

        r'src="\[\[\s*\$application\.path\s*\+\s*[\'"]([^\'"]+)[\'"]\s*\]\]"',

        r'src="\1"',

        html
    )

    # =====================================================
    # remaining bindings
    # =====================================================

    html = re.sub(

        r'\[\[.*?\]\]',

        '',

        html
    )

    return html


# =========================================================
# BUILD COMPLETE HTML
# =========================================================

def build_complete_html(
    shell_html,
    page_html,
    global_css
):

    vb_base_css = load_vb_base_css()

    final_css = f"""

    {vb_base_css}

    {global_css}

    """

    # =====================================================
    # CLEAN
    # =====================================================

    shell_html = clean_html(
        shell_html
    )

    page_html = clean_html(
        page_html
    )

    shell_html = fix_image_paths(
        shell_html
    )

    page_html = fix_image_paths(
        page_html
    )

    # =====================================================
    # SPLIT HEADER / FOOTER
    # =====================================================

    header_html, footer_html = split_shell(
        shell_html
    )

    # =====================================================
    # TRANSLATE
    # =====================================================

    header_html = translate_oj_html(
        header_html
    )

    footer_html = translate_oj_html(
        footer_html
    )

    page_html = translate_oj_html(
        page_html
    )

    # =====================================================
    # BODY
    # =====================================================

    body_content = f"""
    <div id="vb-shell">

        <div id="vb-header">

            {header_html}

        </div>

        <main id="vb-page-content">

            {page_html}

        </main>

        <div id="vb-footer">

            {footer_html}

        </div>

    </div>
    """

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
            min-height:100%;
        }}

        body {{
            margin:0;
            padding:0;
            background:#ffffff;
            font-family:Arial, Helvetica, sans-serif;
            width:100%;
            min-height:100vh;
            overflow-x:hidden;
        }}

        #vb-shell {{
            width:100%;
            min-height:100vh;
            display:flex;
            flex-direction:column;
        }}

        #vb-header {{
            width:100%;
            flex-shrink:0;
        }}

        #vb-page-content {{
            width:100%;
            flex:1;
            padding:16px;
            display:block;
        }}

        #vb-footer {{
            width:100%;
            margin-top:auto;
            flex-shrink:0;
        }}

        table {{
            border-collapse:collapse;
            width:100%;
        }}

        th {{
            background:#f0f0f0;
            padding:8px;
            border:1px solid #ccc;
            text-align:left;
            font-size:12px;
        }}

        td {{
            padding:8px;
            border:1px solid #ccc;
            font-size:12px;
        }}

        img {{
            max-width:100%;
            display:inline-block;
        }}

        input,
        textarea,
        select,
        button {{
            font-family:Arial;
        }}

        label {{
            display:block;
            margin-bottom:4px;
        }}

        .oj-flex {{
            display:flex;
            flex-wrap:wrap;
            gap:16px;
            width:100%;
            align-items:flex-start;
        }}

        .oj-flex-item {{
            flex:1;
            min-width:0;
        }}

        #vb-page-content > * {{
            width:100%;
        }}

        {final_css}

        </style>

    </head>

    <body>

    {body_content}

    </body>

    </html>
    """

    return final_html


# =========================================================
# SAVE TEMP HTML
# =========================================================

def save_temp_html(
    html_content,
    base_path=None
):

    temp_dir = tempfile.mkdtemp()

    print(
        f"[HTML_RENDERER] temp dir: {temp_dir}"
    )

    # =====================================================
    # COPY RESOURCES
    # =====================================================

    copy_resources(

        temp_dir=
            temp_dir,

        base_path=
            base_path
    )

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

    return html_path


# =========================================================
# RENDER HTML TO PNG
# =========================================================

def render_html_to_png(
    html_path
):

    output_png = os.path.join(

        os.path.dirname(
            html_path
        ),

        "output.png"
    )

    debug_png = os.path.join(

        os.path.dirname(
            html_path
        ),

        "debug.png"
    )

    with sync_playwright() as p:

        browser = p.chromium.launch(

            headless=True
        )

        page = browser.new_page(

            viewport={

                "width": 1600,

                "height": 3000
            }
        )

        page.goto(

            f"file:///{html_path}",

            wait_until="networkidle"
        )

        # =================================================
        # WAIT RENDER
        # =================================================

        page.wait_for_timeout(
            3000
        )

        print(
            "[HTML_RENDERER] page loaded"
        )

        # =================================================
        # DEBUG SCREENSHOT
        # =================================================

        page.screenshot(

            path=debug_png,

            full_page=True
        )

        # =================================================
        # FINAL SCREENSHOT
        # =================================================

        page.screenshot(

            path=output_png,

            full_page=True
        )

        browser.close()

    print(
        f"[HTML_RENDERER] png created: {output_png}"
    )

    return output_png


# =========================================================
# MAIN
# =========================================================

def render_visual_builder_page(
    shell_html,
    page_html,
    global_css,
    base_path=None
):

    complete_html = build_complete_html(

        shell_html=
            shell_html,

        page_html=
            page_html,

        global_css=
            global_css
    )

    html_path = save_temp_html(

        html_content=
            complete_html,

        base_path=
            base_path
    )

    png_path = render_html_to_png(
        html_path
    )

    return png_path