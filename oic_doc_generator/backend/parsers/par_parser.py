# =========================================================
# FILE:
# oic_doc_generator/parsers/par_parser.py
# =========================================================

import zipfile
import tempfile
import os

from io import BytesIO


# =========================================================
# EXTRACT PACKAGE
# =========================================================

def extract_package(
    uploaded_file
):

    temp_dir = tempfile.mkdtemp()

    with zipfile.ZipFile(

        uploaded_file,

        'r'
    ) as zip_ref:

        zip_ref.extractall(
            temp_dir
        )

    return temp_dir


# =========================================================
# GET PAR BINARY CONTENT ZIP
# =========================================================

def get_par_binary_content_zip(
    uploaded_file
):

    uploaded_file.seek(0)

    binary_output = BytesIO()

    with zipfile.ZipFile(

        uploaded_file,

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
# FIND ALL IAR FILES
# =========================================================

def find_all_iar_files(
    base_path
):

    iar_files = []

    for root, dirs, files in os.walk(
        base_path
    ):

        for file in files:

            if file.lower().endswith(
                ".iar"
            ):

                iar_files.append(

                    os.path.join(
                        root,
                        file
                    )
                )

    return iar_files


# =========================================================
# FIND APPLICATION FOLDER
# =========================================================

def find_application_folder(
    base_path,
    application_name
):

    for root, dirs, files in os.walk(
        base_path
    ):

        for d in dirs:

            if (
                d.lower()
                ==
                application_name.lower()
            ):

                return os.path.join(
                    root,
                    d
                )

    return None


# =========================================================
# FIND FILE
# =========================================================

def find_file(
    base_path,
    filename
):

    for root, dirs, files in os.walk(
        base_path
    ):

        for file in files:

            if (
                file.lower()
                ==
                filename.lower()
            ):

                return os.path.join(
                    root,
                    file
                )

    return None


# =========================================================
# FIND JCA FILE
# =========================================================

def find_jca_file(
    application_folder
):

    if not application_folder:

        return None

    for root, dirs, files in os.walk(
        application_folder
    ):

        for file in files:

            if file.endswith(
                ".jca"
            ):

                return os.path.join(
                    root,
                    file
                )

    return None


# =========================================================
# BUILD APPLICATION MAP
# =========================================================

def build_application_map(
    applications
):

    return {

        app["Application"]: app

        for app in applications
    }