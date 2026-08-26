# =========================================================
# FILE:
# oic_doc_generator/utils/sql_exporter.py
# =========================================================

import os
import zipfile
import tempfile
import shutil
import uuid


# =========================================================
# CREATE DELIVERY FOLDER
# =========================================================

def create_delivery_folder():

    root_folder = os.path.join(

        tempfile.gettempdir(),

        "oic_delivery_"

        + str(uuid.uuid4())
    )

    os.makedirs(
        root_folder,
        exist_ok=True
    )

    sql_folder = os.path.join(
        root_folder,
        "SQL"
    )

    sequences_folder = os.path.join(
        sql_folder,
        "Secuencias"
    )

    packages_folder = os.path.join(
        sql_folder,
        "Packages"
    )

    views_folder = os.path.join(
        sql_folder,
        "Vistas"
    )

    indexes_folder = os.path.join(
        sql_folder,
        "Indices"
    )

    triggers_folder = os.path.join(
        sql_folder,
        "Triggers"
    )

    os.makedirs(
        sequences_folder,
        exist_ok=True
    )

    os.makedirs(
        packages_folder,
        exist_ok=True
    )

    os.makedirs(
        views_folder,
        exist_ok=True
    )

    os.makedirs(
        indexes_folder,
        exist_ok=True
    )

    os.makedirs(
        triggers_folder,
        exist_ok=True
    )

    return {

        "root":
            root_folder,

        "sql":
            sql_folder,

        "sequences":
            sequences_folder,

        "packages":
            packages_folder,

        "views":
            views_folder,

        "indexes":
            indexes_folder,

        "triggers":
            triggers_folder
    }


# =========================================================
# SAFE FILE NAME
# =========================================================

def safe_file_name(
    value
):

    if not value:

        return "object"

    invalid_chars = [

        "\\",
        "/",
        ":",
        "*",
        "?",
        '"',
        "<",
        ">",
        "|"
    ]

    result = value

    for char in invalid_chars:

        result = result.replace(
            char,
            "_"
        )

    return result.strip()


# =========================================================
# EXPORT SEQUENCE SQL
# =========================================================

def export_sequence_sql(
    sequence,
    output_folder
):

    sequence_name = safe_file_name(

        sequence.get(
            "sequence_name",
            "sequence"
        )
    )

    file_path = os.path.join(

        output_folder,

        f"{sequence_name}.sql"
    )

    sql_text = sequence.get(
        "sql",
        ""
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            sql_text
        )

    return file_path


# =========================================================
# EXPORT ALL SEQUENCES
# =========================================================

def export_sequences(
    sequences,
    output_folder
):

    result = {}

    for sequence in sequences:

        file_path = export_sequence_sql(

            sequence,

            output_folder
        )

        result[
            sequence.get(
                "sequence_name",
                ""
            )
        ] = file_path

    return result


# =========================================================
# EXPORT PACKAGE SPEC
# =========================================================

def export_package_spec(
    package,
    output_folder
):

    package_name = safe_file_name(

        package.get(
            "package_name",
            "package"
        )
    )

    file_path = os.path.join(

        output_folder,

        f"{package_name}_spec.sql"
    )

    sql_text = package.get(
        "package_spec",
        ""
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            sql_text
        )

    return file_path


# =========================================================
# EXPORT PACKAGE BODY
# =========================================================

def export_package_body(
    package,
    output_folder
):

    package_name = safe_file_name(

        package.get(
            "package_name",
            "package"
        )
    )

    file_path = os.path.join(

        output_folder,

        f"{package_name}_body.sql"
    )

    sql_text = package.get(
        "package_body",
        ""
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            sql_text
        )

    return file_path


# =========================================================
# EXPORT ALL PACKAGES
# =========================================================

def export_packages(
    packages,
    output_folder
):

    result = {}

    for package in packages:

        spec_path = export_package_spec(

            package,

            output_folder
        )

        body_path = export_package_body(

            package,

            output_folder
        )

        result[
            package.get(
                "package_name",
                ""
            )
        ] = {

            "spec":
                spec_path,

            "body":
                body_path
        }

    return result

# =========================================================
# EXPORT VIEW SQL
# =========================================================

def export_view_sql(
    view,
    output_folder
):

    view_name = safe_file_name(
        view.get(
            "view_name",
            "view"
        )
    )

    file_path = os.path.join(
        output_folder,
        f"{view_name}.sql"
    )

    sql_text = view.get(
        "sql",
        ""
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            sql_text
        )

    return file_path


# =========================================================
# EXPORT ALL VIEWS
# =========================================================

def export_views(
    views,
    output_folder
):

    result = {}

    for view in views:

        file_path = export_view_sql(
            view,
            output_folder
        )

        result[
            view.get(
                "view_name",
                ""
            )
        ] = file_path

    return result


# =========================================================
# EXPORT INDEX SQL
# =========================================================

def export_index_sql(
    index,
    output_folder
):

    index_name = safe_file_name(
        index.get(
            "index_name",
            "index"
        )
    )

    file_path = os.path.join(
        output_folder,
        f"{index_name}.sql"
    )

    sql_text = index.get(
        "sql",
        ""
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            sql_text
        )

    return file_path


# =========================================================
# EXPORT ALL INDEXES
# =========================================================

def export_indexes(
    indexes,
    output_folder
):

    result = {}

    for index in indexes:

        file_path = export_index_sql(
            index,
            output_folder
        )

        result[
            index.get(
                "index_name",
                ""
            )
        ] = file_path

    return result


# =========================================================
# EXPORT TRIGGER SQL
# =========================================================

def export_trigger_sql(
    trigger,
    output_folder
):

    trigger_name = safe_file_name(
        trigger.get(
            "trigger_name",
            "trigger"
        )
    )

    file_path = os.path.join(
        output_folder,
        f"{trigger_name}.sql"
    )

    sql_text = trigger.get(
        "sql",
        ""
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            sql_text
        )

    return file_path


# =========================================================
# EXPORT ALL TRIGGERS
# =========================================================

def export_triggers(
    triggers,
    output_folder
):

    result = {}

    for trigger in triggers:

        file_path = export_trigger_sql(
            trigger,
            output_folder
        )

        result[
            trigger.get(
                "trigger_name",
                ""
            )
        ] = file_path

    return result


# =========================================================
# EXPORT DATABASE SQL
# =========================================================

def export_database_sql(
    metadata
):

    folders = create_delivery_folder()


    # =====================================================
    # SEQUENCES
    # =====================================================

    sequence_files = export_sequences(

        metadata.get(
            "sequences",
            []
        ),

        folders["sequences"]
    )


    # =====================================================
    # PACKAGES
    # =====================================================

    package_files = export_packages(

        metadata.get(
            "packages",
            []
        ),

        folders["packages"]
    )


    # =====================================================
    # VIEWS
    # =====================================================

    view_files = export_views(

        metadata.get(
            "views",
            []
        ),

        folders["views"]
    )


    # =====================================================
    # INDEXES
    # =====================================================

    index_files = export_indexes(

        metadata.get(
            "indexes",
            []
        ),

        folders["indexes"]
    )


    # =====================================================
    # TRIGGERS
    # =====================================================

    trigger_files = export_triggers(

        metadata.get(
            "triggers",
            []
        ),

        folders["triggers"]
    )


    return {

        "root":
            folders["root"],

        "sequence_files":
            sequence_files,

        "package_files":
            package_files,

        "view_files":
            view_files,

        "index_files":
            index_files,

        "trigger_files":
            trigger_files
    }


# =========================================================
# CREATE DELIVERY ZIP
# =========================================================

def create_delivery_zip(
    delivery_folder,
    output_zip_path
):

    with zipfile.ZipFile(

        output_zip_path,

        "w",

        zipfile.ZIP_DEFLATED

    ) as zip_file:

        for root, dirs, files in os.walk(
            delivery_folder
        ):

            for file in files:

                # =====================================
                # IGNORE ZIP FILES
                # =====================================

                if file.lower().endswith(
                    ".zip"
                ):
                    continue

                full_path = os.path.join(
                    root,
                    file
                )

                arc_name = os.path.relpath(

                    full_path,

                    delivery_folder
                )

                zip_file.write(

                    full_path,

                    arc_name
                )

    return output_zip_path

# =========================================================
# CLEAN DELIVERY FOLDER
# =========================================================

def clean_delivery_folder(
    folder
):

    if not folder:

        return

    if not os.path.exists(
        folder
    ):

        return

    try:

        shutil.rmtree(
            folder
        )

    except:

        pass