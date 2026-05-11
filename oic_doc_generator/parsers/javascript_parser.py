# =========================================================
# FILE: oic_doc_generator/parsers/javascript_parser.py
# =========================================================

import os


# =========================================================
# GET JAVASCRIPT FILES
# =========================================================

def get_javascript_files(
    extracted_iar
):

    result = []

    # =====================================================
    # SEARCH APILIBRARY
    # =====================================================

    for root, dirs, files in os.walk(
        extracted_iar
    ):

        if "apilibrary" in root.lower():

            for file in files:

                if file.lower().endswith(
                    ".js"
                ):

                    result.append({

                        "name":
                            file,

                        "path":
                            os.path.join(
                                root,
                                file
                            )
                    })

    return result


# =========================================================
# HAS JAVASCRIPT
# =========================================================

def has_javascript(
    extracted_iar
):

    js_files = get_javascript_files(
        extracted_iar
    )

    return (
        len(js_files) > 0
    )


# =========================================================
# GET JAVASCRIPT NAMES
# =========================================================

def get_javascript_names(
    extracted_iar
):

    result = []

    js_files = get_javascript_files(
        extracted_iar
    )

    for js in js_files:

        result.append(
            js["name"]
        )

    return result