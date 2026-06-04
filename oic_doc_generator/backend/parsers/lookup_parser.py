# =========================================================
# FILE: oic_doc_generator/parsers/lookup_parser.py
# =========================================================

import os


# =========================================================
# GET LOOKUPS
# =========================================================

def get_lookups(
    extracted_iar
):

    result = []

    # =====================================================
    # SEARCH DVMS FOLDER
    # =====================================================

    for root, dirs, files in os.walk(
        extracted_iar
    ):

        if "dvms" in root.lower():

            for file in files:

                if file.lower().endswith(
                    ".dvm"
                ):

                    lookup_name = (
                        os.path.splitext(
                            file
                        )[0]
                    )

                    result.append({

                        "name":
                            lookup_name,

                        "file":
                            file,

                        "path":
                            os.path.join(
                                root,
                                file
                            )
                    })

    return result


# =========================================================
# HAS LOOKUPS
# =========================================================

def has_lookups(
    extracted_iar
):

    lookups = get_lookups(
        extracted_iar
    )

    return (
        len(lookups) > 0
    )


# =========================================================
# GET LOOKUP NAMES
# =========================================================

def get_lookup_names(
    extracted_iar
):

    result = []

    lookups = get_lookups(
        extracted_iar
    )

    for lookup in lookups:

        result.append(
            lookup["name"]
        )

    return result