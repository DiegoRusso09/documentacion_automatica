# =========================================================
# FILE:
# oic_doc_generator/utils/bip_utils.py
# =========================================================

import os
import shutil
import tempfile
import uuid
from urllib.parse import unquote


# =========================================================
# SUPPORTED EXTENSIONS
# =========================================================

SUPPORTED_BIP_EXTENSIONS = [

    ".xdoz",

    ".xdmz",

    ".xdrz"
]


# =========================================================
# IS BIP FILE
# =========================================================

def is_bip_file(
    file_name
):

    if not file_name:

        return False

    lower = file_name.lower()

    for ext in SUPPORTED_BIP_EXTENSIONS:

        if lower.endswith(ext):

            return True

    return False


# =========================================================
# GET FILE EXTENSION
# =========================================================

def get_file_extension(
    file_name
):

    if not file_name:

        return ""

    return os.path.splitext(
        file_name
    )[1].lower()


# =========================================================
# NORMALIZE REPORT NAME
# =========================================================

def normalize_report_name(
    value
):

    if not value:

        return ""

    value = value.strip()

    value = value.replace(
        ".xdo",
        ""
    )

    value = value.replace(
        ".xdoz",
        ""
    )

    return value.strip()


# =========================================================
# NORMALIZE DM NAME
# =========================================================

def normalize_dm_name(
    value
):

    if not value:

        return ""

    value = value.strip()

    value = value.replace(
        ".xdm",
        ""
    )

    value = value.replace(
        ".xdmz",
        ""
    )

    return value.strip()


# =========================================================
# DECODE BIP PATH
# =========================================================

def decode_bip_path(
    value
):

    if not value:

        return ""

    decoded = unquote(
        value
    )

    decoded = decoded.replace(
        "+",
        " "
    )

    return decoded


# =========================================================
# SAFE CREATE DIRECTORY
# =========================================================

def safe_create_directory(
    folder_path
):

    if not folder_path:

        return

    os.makedirs(
        folder_path,
        exist_ok=True
    )


# =========================================================
# CREATE TEMP DIRECTORY
# =========================================================

def create_temp_directory(
    prefix="bip_"
):

    folder = os.path.join(

        tempfile.gettempdir(),

        prefix + str(uuid.uuid4())
    )

    safe_create_directory(
        folder
    )

    return folder


# =========================================================
# SAFE REMOVE DIRECTORY
# =========================================================

def safe_remove_directory(
    folder_path
):

    if not folder_path:

        return

    if not os.path.exists(
        folder_path
    ):

        return

    try:

        shutil.rmtree(
            folder_path
        )

    except:

        pass


# =========================================================
# FIND FILE RECURSIVE
# =========================================================

def find_file_recursive(
    root_folder,
    target_file
):

    if not root_folder:

        return None

    if not os.path.exists(
        root_folder
    ):

        return None

    for root, dirs, files in os.walk(
        root_folder
    ):

        for file in files:

            if (

                file.lower()

                ==

                target_file.lower()
            ):

                return os.path.join(
                    root,
                    file
                )

    return None


# =========================================================
# FIND FILES BY EXTENSION
# =========================================================

def find_files_by_extension(
    root_folder,
    extension
):

    result = []

    if not root_folder:

        return result

    if not os.path.exists(
        root_folder
    ):

        return result

    for root, dirs, files in os.walk(
        root_folder
    ):

        for file in files:

            if file.lower().endswith(
                extension.lower()
            ):

                result.append(

                    os.path.join(
                        root,
                        file
                    )
                )

    return result


# =========================================================
# SAFE READ TEXT FILE
# =========================================================

def safe_read_text_file(
    file_path
):

    if not file_path:

        return ""

    if not os.path.exists(
        file_path
    ):

        return ""

    encodings = [

        "utf-8",

        "utf-16",

        "latin-1"
    ]

    for encoding in encodings:

        try:

            with open(

                file_path,

                "r",

                encoding=encoding,

                errors="ignore"
            ) as file:

                return file.read()

        except:

            continue

    return ""


# =========================================================
# GET FILE NAME WITHOUT EXTENSION
# =========================================================

def get_file_name_without_extension(
    file_name
):

    if not file_name:

        return ""

    return os.path.splitext(
        os.path.basename(file_name)
    )[0]


# =========================================================
# SAFE JOIN TEXT
# =========================================================

def safe_join_text(
    values,
    separator=", "
):

    cleaned = []

    for value in values:

        if not value:

            continue

        value = str(value).strip()

        if not value:

            continue

        if value not in cleaned:

            cleaned.append(
                value
            )

    return separator.join(
        cleaned
    )


# =========================================================
# BOOLEAN TO YES NO
# =========================================================

def boolean_to_yes_no(
    value
):

    return (

        "Si"

        if value

        else "No"
    )


# =========================================================
# CLEAN EMPTY VALUES
# =========================================================

def clean_empty_values(
    data
):

    if isinstance(
        data,
        dict
    ):

        result = {}

        for key, value in data.items():

            if value in [

                None,

                "",

                [],

                {}
            ]:

                continue

            result[key] = value

        return result

    return data


# =========================================================
# BUILD WARNING
# =========================================================

def build_warning(
    message
):

    return {

        "type":
            "warning",

        "message":
            message
    }


# =========================================================
# BUILD ERROR
# =========================================================

def build_error(
    message
):

    return {

        "type":
            "error",

        "message":
            message
    }