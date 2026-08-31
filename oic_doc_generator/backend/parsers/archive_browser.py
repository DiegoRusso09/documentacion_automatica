# =========================================================
# FILE:
# oic_doc_generator/backend/parsers/archive_browser.py
# =========================================================

from pathlib import Path

import json
import os
import shutil
import tempfile
import time
import uuid
import zipfile


# =========================================================
# CONFIG
# =========================================================

SESSION_TTL_SECONDS = 30 * 60


SESSION_ROOT = os.path.join(
    tempfile.gettempdir(),
    "documentation_automation_tools"
)


SUPPORTED_EXTENSIONS = {
    ".par",
    ".iar",
    ".xdoz",
    ".xdmz",
    ".xdrz"
}


# =========================================================
# INIT
# =========================================================

os.makedirs(
    SESSION_ROOT,
    exist_ok=True
)


# =========================================================
# SESSION PATH
# =========================================================

def get_session_path(
    session_id
):

    if not session_id:
        return None


    # Evitar path traversal
    safe_session_id = (
        os.path.basename(
            session_id
        )
    )


    return os.path.join(
        SESSION_ROOT,
        safe_session_id
    )


# =========================================================
# CLEAN EXPIRED SESSIONS
# =========================================================

def cleanup_expired_sessions():

    if not os.path.exists(
        SESSION_ROOT
    ):
        return


    current_time = time.time()


    for session_name in os.listdir(
        SESSION_ROOT
    ):

        session_path = os.path.join(
            SESSION_ROOT,
            session_name
        )


        if not os.path.isdir(
            session_path
        ):
            continue


        try:

            modified_time = os.path.getmtime(
                session_path
            )


            age = (
                current_time
                -
                modified_time
            )


            if age > SESSION_TTL_SECONDS:

                shutil.rmtree(
                    session_path,
                    ignore_errors=True
                )

        except Exception:

            continue


# =========================================================
# SAFE ZIP EXTRACTION
# =========================================================

def safe_extract_zip(
    archive_path,
    destination
):

    destination_real = os.path.realpath(
        destination
    )


    with zipfile.ZipFile(
        archive_path,
        "r"
    ) as zip_file:

        for member in zip_file.infolist():

            target_path = os.path.realpath(
                os.path.join(
                    destination,
                    member.filename
                )
            )


            # =============================================
            # SECURITY:
            # prevent ../../ outside destination
            # =============================================

            if not (
                target_path
                ==
                destination_real

                or

                target_path.startswith(
                    destination_real
                    +
                    os.sep
                )
            ):

                raise ValueError(
                    "El archivo contiene una ruta no permitida: "
                    +
                    member.filename
                )


        zip_file.extractall(
            destination
        )


# =========================================================
# FILE TYPE
# =========================================================

def get_file_type(
    file_name
):

    extension = (
        Path(
            file_name
        )
        .suffix
        .lower()
    )


    types = {

        ".par":
            "PAR",

        ".iar":
            "IAR",

        ".xdoz":
            "XDOZ",

        ".xdmz":
            "XDMZ",

        ".xdrz":
            "XDRZ"
    }


    return types.get(
        extension,
        "UNKNOWN"
    )


# =========================================================
# BUILD TREE
# =========================================================

def build_directory_tree(
    root_folder,
    current_folder=None
):

    if current_folder is None:
        current_folder = root_folder


    result = []


    try:

        entries = sorted(
            os.listdir(
                current_folder
            ),
            key=lambda item: (
                not os.path.isdir(
                    os.path.join(
                        current_folder,
                        item
                    )
                ),
                item.lower()
            )
        )

    except Exception:

        return result


    for entry in entries:

        full_path = os.path.join(
            current_folder,
            entry
        )


        relative_path = os.path.relpath(
            full_path,
            root_folder
        )


        relative_path = (
            relative_path
            .replace(
                "\\",
                "/"
            )
        )


        # =================================================
        # FOLDER
        # =================================================

        if os.path.isdir(
            full_path
        ):

            result.append({

                "name":
                    entry,

                "type":
                    "folder",

                "path":
                    relative_path,

                "children":
                    build_directory_tree(
                        root_folder,
                        full_path
                    )
            })


        # =================================================
        # FILE
        # =================================================

        else:

            try:

                size = os.path.getsize(
                    full_path
                )

            except Exception:

                size = 0


            extension = (
                Path(
                    entry
                )
                .suffix
                .lower()
            )


            result.append({

                "name":
                    entry,

                "type":
                    "file",

                "path":
                    relative_path,

                "extension":
                    extension,

                "size":
                    size,

                "is_oracle_archive":
                    extension
                    in
                    SUPPORTED_EXTENSIONS
            })


    return result


# =========================================================
# COUNT ITEMS
# =========================================================

def count_tree_items(
    tree
):

    files = 0
    folders = 0


    for item in tree:

        if item.get(
            "type"
        ) == "folder":

            folders += 1


            child_files, child_folders = (
                count_tree_items(
                    item.get(
                        "children",
                        []
                    )
                )
            )


            files += child_files
            folders += child_folders

        else:

            files += 1


    return files, folders


# =========================================================
# CREATE SESSION
# =========================================================

def create_archive_session(
    uploaded_file,
    original_name
):

    cleanup_expired_sessions()


    if not original_name:

        raise ValueError(
            "No se recibió el nombre del archivo."
        )


    extension = (
        Path(
            original_name
        )
        .suffix
        .lower()
    )


    if extension not in SUPPORTED_EXTENSIONS:

        raise ValueError(
            "Tipo de archivo no soportado: "
            +
            extension
        )


    session_id = str(
        uuid.uuid4()
    )


    session_path = os.path.join(
        SESSION_ROOT,
        session_id
    )


    source_folder = os.path.join(
        session_path,
        "source"
    )


    extracted_folder = os.path.join(
        session_path,
        "extracted"
    )


    os.makedirs(
        source_folder,
        exist_ok=True
    )


    os.makedirs(
        extracted_folder,
        exist_ok=True
    )


    source_path = os.path.join(
        source_folder,
        os.path.basename(
            original_name
        )
    )


    # =====================================================
    # SAVE UPLOAD
    # =====================================================

    uploaded_file.seek(
        0
    )


    with open(
        source_path,
        "wb"
    ) as output:

        shutil.copyfileobj(
            uploaded_file,
            output
        )


    # =====================================================
    # VALIDATE ZIP
    # =====================================================

    if not zipfile.is_zipfile(
        source_path
    ):

        shutil.rmtree(
            session_path,
            ignore_errors=True
        )

        raise ValueError(
            "El archivo no contiene una estructura ZIP válida."
        )


    # =====================================================
    # EXTRACT
    # =====================================================

    safe_extract_zip(
        source_path,
        extracted_folder
    )


    # =====================================================
    # TREE
    # =====================================================

    tree = build_directory_tree(
        extracted_folder
    )


    files_count, folders_count = (
        count_tree_items(
            tree
        )
    )


    # =====================================================
    # SESSION METADATA
    # =====================================================

    session_metadata = {

        "session_id":
            session_id,

        "file_name":
            os.path.basename(
                original_name
            ),

        "archive_type":
            get_file_type(
                original_name
            ),

        "created_at":
            int(
                time.time()
            ),

        "expires_in":
            SESSION_TTL_SECONDS,

        "files_count":
            files_count,

        "folders_count":
            folders_count
    }


    metadata_path = os.path.join(
        session_path,
        "session.json"
    )


    with open(
        metadata_path,
        "w",
        encoding="utf-8"
    ) as metadata_file:

        json.dump(
            session_metadata,
            metadata_file,
            indent=4,
            ensure_ascii=False
        )


    # Touch para reiniciar TTL
    os.utime(
        session_path,
        None
    )


    return {

        **session_metadata,

        "tree":
            tree
    }


# =========================================================
# GET FILE FROM SESSION
# =========================================================

def get_session_file(
    session_id,
    relative_path
):

    cleanup_expired_sessions()


    session_path = get_session_path(
        session_id
    )


    if (
        not session_path
        or
        not os.path.isdir(
            session_path
        )
    ):

        raise FileNotFoundError(
            "La sesión no existe o ha expirado."
        )


    extracted_folder = os.path.join(
        session_path,
        "extracted"
    )


    requested_path = os.path.realpath(
        os.path.join(
            extracted_folder,
            relative_path
        )
    )


    extracted_real = os.path.realpath(
        extracted_folder
    )


    # =====================================================
    # SECURITY
    # =====================================================

    if not requested_path.startswith(
        extracted_real
        +
        os.sep
    ):

        raise ValueError(
            "Ruta de archivo no permitida."
        )


    if not os.path.isfile(
        requested_path
    ):

        raise FileNotFoundError(
            "El archivo solicitado no existe."
        )


    # Renovamos actividad de la sesión
    os.utime(
        session_path,
        None
    )


    return requested_path