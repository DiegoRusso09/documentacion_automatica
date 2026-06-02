# =========================================================
# FILE:
# oic_doc_generator/parsers/iar_parser.py
# =========================================================

import zipfile
import tempfile
import os

from io import BytesIO

from oic_doc_generator.parsers.par_parser import (
    find_all_iar_files,
    find_application_folder,
    find_jca_file,
    find_file,
    build_application_map
)


# =========================================================
# EXTRACT IAR
# =========================================================

def extract_iar(
    iar_path
):

    temp_dir = tempfile.mkdtemp()

    # =====================================================
    # STREAMLIT FILE
    # =====================================================

    if hasattr(
        iar_path,
        "read"
    ):

        iar_path.seek(0)

        with zipfile.ZipFile(

            iar_path,

            'r'
        ) as zip_ref:

            zip_ref.extractall(
                temp_dir
            )

    # =====================================================
    # FILE PATH
    # =====================================================

    else:

        with zipfile.ZipFile(

            iar_path,

            'r'
        ) as zip_ref:

            zip_ref.extractall(
                temp_dir
            )

    return temp_dir


# =========================================================
# GET IAR BINARY CONTENT ZIP
# =========================================================

def get_iar_binary_content_zip(
    uploaded_iar
):

    uploaded_iar.seek(0)

    binary_output = BytesIO()

    with zipfile.ZipFile(

        uploaded_iar,

        'r'
    ) as source_zip:

        with zipfile.ZipFile(

            binary_output,

            'w',

            zipfile.ZIP_DEFLATED
        ) as target_zip:

            for file_info in source_zip.infolist():

                binary_content = source_zip.read(
                    file_info.filename
                )

                target_zip.writestr(

                    file_info.filename,

                    binary_content
                )

    binary_output.seek(0)

    return binary_output.getvalue()


# =========================================================
# REEXPORTS
# =========================================================

__all__ = [

    "extract_iar",

    "get_iar_binary_content_zip",

    "find_all_iar_files",

    "find_application_folder",

    "find_jca_file",

    "find_file",

    "build_application_map"
]