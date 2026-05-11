# =========================================================
# FILE:
# oic_doc_generator/parsers/vb_parser.py
# =========================================================

import os

from parsers.vb_extractor import (
    read_text_file
)


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

        "test"
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
                    html
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