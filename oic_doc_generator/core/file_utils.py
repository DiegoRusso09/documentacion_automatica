# =========================================================
# core/file_utils.py
# =========================================================

import os
import zipfile
import tempfile
import shutil


# =========================================================
# EXTRACT ZIP FILE
# =========================================================

def extract_zip(zip_path_or_file):

    temp_dir = tempfile.mkdtemp()

    with zipfile.ZipFile(
        zip_path_or_file,
        'r'
    ) as zip_ref:

        zip_ref.extractall(temp_dir)

    return temp_dir


# =========================================================
# EXTRACT PAR
# =========================================================

def extract_par(uploaded_file):

    return extract_zip(
        uploaded_file
    )


# =========================================================
# EXTRACT IAR
# =========================================================

def extract_iar(iar_path):

    return extract_zip(
        iar_path
    )


# =========================================================
# FIND FILE
# =========================================================

def find_file(
    base_path,
    filename
):

    for root, dirs, files in os.walk(base_path):

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
# FIND FILES BY EXTENSION
# =========================================================

def find_files_by_extension(
    base_path,
    extension
):

    results = []

    for root, dirs, files in os.walk(base_path):

        for file in files:

            if (
                file.lower().endswith(
                    extension.lower()
                )
            ):

                results.append(
                    os.path.join(
                        root,
                        file
                    )
                )

    return results


# =========================================================
# FIND DIRECTORY
# =========================================================

def find_directory(
    base_path,
    directory_name
):

    for root, dirs, files in os.walk(base_path):

        for d in dirs:

            if (
                d.lower()
                ==
                directory_name.lower()
            ):

                return os.path.join(
                    root,
                    d
                )

    return None


# =========================================================
# READ TEXT FILE
# =========================================================

def read_text_file(file_path):

    if not file_path:
        return ""

    if not os.path.exists(file_path):
        return ""

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            return f.read()

    except Exception:

        return ""


# =========================================================
# READ BINARY FILE
# =========================================================

def read_binary_file(file_path):

    if not file_path:
        return b""

    if not os.path.exists(file_path):
        return b""

    try:

        with open(
            file_path,
            "rb"
        ) as f:

            return f.read()

    except Exception:

        return b""


# =========================================================
# CREATE ZIP FROM DIRECTORY
# =========================================================

def create_zip_from_directory(
    directory_path,
    output_zip_path
):

    with zipfile.ZipFile(
        output_zip_path,
        'w',
        zipfile.ZIP_DEFLATED
    ) as zipf:

        for root, dirs, files in os.walk(directory_path):

            for file in files:

                file_path = os.path.join(
                    root,
                    file
                )

                arcname = os.path.relpath(
                    file_path,
                    directory_path
                )

                zipf.write(
                    file_path,
                    arcname
                )

    return output_zip_path


# =========================================================
# LIST DIRECTORY TREE
# =========================================================

def list_directory_tree(base_path):

    results = []

    for root, dirs, files in os.walk(base_path):

        level = root.replace(
            base_path,
            ''
        ).count(os.sep)

        indent = ' ' * 4 * level

        results.append(
            f"{indent}{os.path.basename(root)}/"
        )

        sub_indent = ' ' * 4 * (
            level + 1
        )

        for file in files:

            results.append(
                f"{sub_indent}{file}"
            )

    return "\n".join(results)


# =========================================================
# CLEAN TEMP DIRECTORY
# =========================================================

def remove_directory(directory_path):

    if (
        directory_path
        and
        os.path.exists(directory_path)
    ):

        shutil.rmtree(
            directory_path,
            ignore_errors=True
        )