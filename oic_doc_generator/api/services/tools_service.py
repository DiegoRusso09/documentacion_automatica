# =========================================================
# FILE:
# oic_doc_generator/api/services/tools_service.py
# =========================================================

import zipfile

from io import BytesIO

from oic_doc_generator.backend.parsers.par_parser import (
    get_par_binary_content_zip
)

from oic_doc_generator.backend.parsers.iar_parser import (
    get_iar_binary_content_zip
)

from oic_doc_generator.backend.parsers.bip_archive_parser import (
    build_bip_artifact_tree
)

from oic_doc_generator.backend.parsers.bip_metadata_builder import (
    build_bip_metadata
)


# =========================================================
# ZIP TREE
# =========================================================

def build_zip_tree(
    binary_content
):

    result = []

    with zipfile.ZipFile(
        BytesIO(binary_content),
        "r"
    ) as zip_file:

        for item in zip_file.namelist():

            result.append(item)

    return result


# =========================================================
# PAR
# =========================================================

def extract_par_service(
    uploaded_file
):

    binary_content = (
        get_par_binary_content_zip(
            uploaded_file
        )
    )

    return {

        "type": "PAR",

        "files": build_zip_tree(
            binary_content
        )
    }


# =========================================================
# IAR
# =========================================================

def extract_iar_service(
    uploaded_file
):

    binary_content = (
        get_iar_binary_content_zip(
            uploaded_file
        )
    )

    return {

        "type": "IAR",

        "files": build_zip_tree(
            binary_content
        )
    }


# =========================================================
# OTBI
# =========================================================

def extract_otbi_service(
    uploaded_file
):

    artifact_tree = (
        build_bip_artifact_tree(
            [uploaded_file]
        )
    )

    metadata = (
        build_bip_metadata(
            artifact_tree
        )
    )

    return {

        "type": "OTBI",

        "artifact_tree": artifact_tree,

        "metadata": metadata
    }