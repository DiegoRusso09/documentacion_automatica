# =========================================================
# FILE:
# oic_doc_generator/api/services/tools_service.py
# =========================================================

from oic_doc_generator.backend.parsers.archive_browser import (
    create_archive_session,
    get_session_file
)


# =========================================================
# EXPLORE ARCHIVE
# =========================================================

def explore_archive_service(
    uploaded_file,
    original_name
):

    return create_archive_session(
        uploaded_file=
            uploaded_file,

        original_name=
            original_name
    )


# =========================================================
# DOWNLOAD FILE
# =========================================================

def download_archive_file_service(
    session_id,
    file_path
):

    return get_session_file(
        session_id=
            session_id,

        relative_path=
            file_path
    )