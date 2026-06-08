# =========================================================
# FILE:
# oic_doc_generator/parsers/vb_parser.py
# =========================================================

import os
from bs4 import BeautifulSoup
import re

from oic_doc_generator.backend.parsers.vb_extractor import (
    read_text_file
)


# =========================================================
# EXTRACT BUTTONS
# =========================================================

def extract_buttons(
    html
):

    result = []

    if not html:

        return result

    try:

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

    except:

        return result

    buttons = soup.find_all(
        "oj-button"
    )

    for button in buttons:

        label = button.get(
            "label",
            ""
        ).strip()

        if not label:

            continue

        result.append({

            "name": label,

            "description": ""
        })

    return result


# =========================================================
# EXTRACT TABLE COLUMNS
# =========================================================

def extract_table_columns(
    html
):

    result = []

    if not html:

        return result

    try:

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

    except:

        return result

    seen = set()

    # =====================================================
    # TABLES
    # =====================================================

    tables = soup.find_all(
        "oj-table"
    )

    for table in tables:

        columns = table.get(
            "columns",
            ""
        )

        if not columns:

            continue

        # =================================================
        # FIND HEADERTEXT
        # =================================================

        matches = re.findall(

            r'headerText\s*:\s*[\'"]([^\'"]+)',

            columns
        )

        for header in matches:

            clean = header.strip()

            if not clean:

                continue

            if clean in seen:

                continue

            seen.add(clean)

            result.append({

                "name": clean,

                "description": ""
            })

    # =====================================================
    # INPUTS
    # =====================================================

    inputs = soup.find_all([

        "oj-input-text",

        "oj-input-number",

        "oj-input-date",

        "oj-combobox-one"
    ])

    for inp in inputs:

        label = inp.get(
            "label-hint",
            ""
        ).strip()

        if not label:

            continue

        if label in seen:

            continue

        seen.add(label)

        result.append({

            "name": label,

            "description": ""
        })

    return result


# =========================================================
# VALID HTML FILE
# =========================================================

def is_html_file(
    file_name
):

    if not file_name:

        return False

    return file_name.lower().endswith(
        ".html"
    )


# =========================================================
# IGNORE FILE
# =========================================================

def should_ignore_file(
    file_name,
    full_path
):

    lower_name = file_name.lower()

    lower_path = full_path.lower()

    # =====================================================
    # IGNORE SHELL
    # =====================================================

    if lower_name == "shell-page.html":

        return True

    # =====================================================
    # IGNORE COMMON IRRELEVANT FILES
    # =====================================================

    ignored_words = [

        "fragment",

        "metadata",

        "template",

        "component",

        "test",

        "index",

        "root",

        "router",

        "layout",

        "loader",

        "bootstrap",

        "navigation",

        "menu",

        "/js/",

        "/css/",

        "/images/",

        "/resources/"
    ]

    for word in ignored_words:

        if word in lower_path:

            return True

    return False


# =========================================================
# VALID VB CONTENT
# =========================================================

def contains_visual_builder_content(
    html
):

    if not html:

        return False

    cleaned = html.strip()

    if not cleaned:

        return False

    indicators = [

        "oj-",

        "oj-bind",

        "oj-validation-group",

        "oj-defer",

        "<template",

        "<div",

        "<span",

        "<form",

        "vbcs"
    ]

    for indicator in indicators:

        if indicator.lower() in cleaned.lower():

            return True

    return False


# =========================================================
# GENERATE SCREEN NAME
# =========================================================

def generate_screen_name(
    file_name
):

    name = file_name

    name = name.replace(
        ".html",
        ""
    )

    name = name.replace(
        "-page",
        ""
    )

    name = name.replace(
        "_",
        " "
    )

    name = name.replace(
        "-",
        " "
    )

    words = name.split()

    words = [

        word.capitalize()

        for word in words
    ]

    final_name = " ".join(
        words
    )

    if not final_name.strip():

        final_name = "Pantalla"

    return final_name


# =========================================================
# FIND HTML PAGES
# =========================================================

def find_visual_builder_pages(
    application_folder
):

    result = []

    if not application_folder:

        return result

    print(
        f"[VB_PARSER] buscando páginas en: {application_folder}"
    )

    for root, dirs, files in os.walk(
        application_folder
    ):

        # =================================================
        # IGNORE HEAVY DIRECTORIES
        # =================================================

        ignored_dirs = [

            ".git",

            "node_modules",

            "images",

            "css"
        ]

        dirs[:] = [

            d for d in dirs

            if d not in ignored_dirs
        ]

        for file in files:

            # =============================================
            # ONLY HTML
            # =============================================

            if not is_html_file(
                file
            ):

                continue

            full_path = os.path.join(
                root,
                file
            )

            # =============================================
            # IGNORE FILE
            # =============================================

            if should_ignore_file(

                file,

                full_path
            ):

                continue

            # =============================================
            # READ HTML
            # =============================================

            html = read_text_file(
                full_path
            )

            if not html:

                continue

            # =============================================
            # VALID VB PAGE
            # =============================================

            if not contains_visual_builder_content(
                html
            ):

                continue

            page_data = {

                "name":
                    generate_screen_name(
                        file
                    ),

                "file_name":
                    file,

                "path":
                    full_path,

                "html":
                    html,

                "buttons":
                    extract_buttons(
                        html
                    ),

                "table_columns":
                    extract_table_columns(
                        html
                    )
            }

            result.append(
                page_data
            )

            print(
                f"[VB_PARSER] página encontrada: {file}"
            )

    # =====================================================
    # SORT
    # =====================================================

    result.sort(

        key=lambda x: x["file_name"]
    )

    print(
        f"[VB_PARSER] total páginas: {len(result)}"
    )

    return result


# =========================================================
# BUILD PAGE METADATA
# =========================================================

def build_page_metadata(
    extraction_metadata
):

    if not extraction_metadata:

        raise Exception(
            "extraction_metadata vacío"
        )

    application_folder = extraction_metadata.get(
        "application_folder"
    )

    pages = find_visual_builder_pages(
        application_folder
    )

    result = {

        "root_path":
            extraction_metadata.get(
                "root_path"
            ),

        "application_folder":
            application_folder,

        "resources_path":
            extraction_metadata.get(
                "resources_path"
            ),

        "images_path":
            extraction_metadata.get(
                "images_path"
            ),

        "app_css":
            extraction_metadata.get(
                "app_css",
                ""
            ),

        "shell_html":
            extraction_metadata.get(
                "shell_html",
                ""
            ),

        "pages":
            pages
    }

    print(
        "[VB_PARSER] metadata de páginas generado"
    )

    return result

