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

    scripts_folder = os.path.join(
        root_folder,
        "scripts"
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
        scripts_folder,
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

        "scripts":
            scripts_folder,

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
# NORMALIZE DATABASE OBJECT NAME
# =========================================================

def normalize_database_object_name(
    value
):

    if not value:

        return ""

    return (
        str(value)
        .replace('"', '')
        .split(".")[-1]
        .strip()
        .upper()
    )


# =========================================================
# SORT TABLES BY FOREIGN KEY DEPENDENCY
# =========================================================

def sort_tables_by_dependencies(
    tables
):

    if not tables:

        return []


    table_map = {}

    original_order = []


    for table in tables:

        table_name = (
            normalize_database_object_name(
                table.get(
                    "table_name",
                    ""
                )
            )
        )


        if not table_name:

            continue


        table_map[
            table_name
        ] = table


        original_order.append(
            table_name
        )


    # =====================================================
    # DEPENDENCIES
    # =====================================================

    dependencies = {}


    for table_name in original_order:

        table = table_map[
            table_name
        ]


        dependencies[
            table_name
        ] = set()


        for foreign_key in table.get(
            "foreign_keys",
            []
        ):

            referenced_table = (
                normalize_database_object_name(
                    foreign_key.get(
                        "referenced_table",
                        ""
                    )
                )
            )


            if (

                referenced_table

                and

                referenced_table in table_map

                and

                referenced_table != table_name

            ):

                dependencies[
                    table_name
                ].add(
                    referenced_table
                )


    # =====================================================
    # TOPOLOGICAL SORT
    # =====================================================

    result = []

    processed = set()


    while len(
        processed
    ) < len(
        original_order
    ):

        progress = False


        for table_name in original_order:

            if table_name in processed:

                continue


            pending_dependencies = (

                dependencies[
                    table_name
                ]

                -

                processed
            )


            if not pending_dependencies:

                result.append(
                    table_map[
                        table_name
                    ]
                )

                processed.add(
                    table_name
                )

                progress = True


        # =================================================
        # CIRCULAR FK
        # =================================================

        if not progress:

            for table_name in original_order:

                if table_name in processed:

                    continue


                result.append(
                    table_map[
                        table_name
                    ]
                )

                processed.add(
                    table_name
                )


            break


    return result


# =========================================================
# ENSURE SQL TERMINATOR
# =========================================================

def ensure_sql_terminator(
    sql_text
):

    sql_text = (
        sql_text
        or
        ""
    ).strip()


    if not sql_text:

        return ""


    if sql_text.endswith(";"):

        return sql_text


    return (
        sql_text
        +
        ";"
    )


# =========================================================
# ENSURE PL/SQL TERMINATOR
# =========================================================

def ensure_plsql_terminator(
    sql_text
):

    sql_text = (
        sql_text
        or
        ""
    ).strip()


    if not sql_text:

        return ""


    if sql_text.endswith("/"):

        return sql_text


    return (
        sql_text
        +
        "\n/"
    )


# =========================================================
# WRITE CONSOLIDATED SCRIPT
# =========================================================

def write_consolidated_script(
    output_folder,
    file_name,
    entries,
    plsql=False
):

    file_path = os.path.join(
        output_folder,
        file_name
    )


    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        for entry in entries:

            object_name = (
                entry.get(
                    "object_name",
                    ""
                )
            )


            object_type = (
                entry.get(
                    "object_type",
                    ""
                )
            )


            sql_text = (
                entry.get(
                    "sql",
                    ""
                )
            )


            if not sql_text:

                continue


            file.write(
                "-- =========================================================\n"
            )

            file.write(
                f"-- {object_type}: {object_name}\n"
            )

            file.write(
                "-- =========================================================\n\n"
            )


            if plsql:

                file.write(
                    ensure_plsql_terminator(
                        sql_text
                    )
                )

            else:

                file.write(
                    ensure_sql_terminator(
                        sql_text
                    )
                )


            file.write(
                "\n\n"
            )


    return file_path


# =========================================================
# BUILD INSTALLATION SCRIPTS
# =========================================================

def build_installation_scripts(
    metadata,
    scripts_folder
):

    installation_scripts = []

    groups = []


    # =====================================================
    # 1 - SEQUENCES
    # =====================================================

    sequence_entries = []


    for sequence in metadata.get(
        "sequences",
        []
    ):

        sequence_entries.append({

            "object_name":
                sequence.get(
                    "sequence_name",
                    ""
                ),

            "object_type":
                "SEQUENCE",

            "sql":
                sequence.get(
                    "sql",
                    ""
                )
        })


    if sequence_entries:

        groups.append({

            "type":
                "SEQUENCE",

            "file_suffix":
                "Sequences",

            "entries":
                sequence_entries,

            "plsql":
                False
        })


    # =====================================================
    # 2 - TABLES
    # =====================================================

    table_entries = []


    sorted_tables = (
        sort_tables_by_dependencies(
            metadata.get(
                "tables",
                []
            )
        )
    )


    for table in sorted_tables:

        table_entries.append({

            "object_name":
                table.get(
                    "table_name",
                    ""
                ),

            "object_type":
                "TABLE",

            "sql":
                table.get(
                    "sql",
                    ""
                )
        })


    if table_entries:

        groups.append({

            "type":
                "TABLE",

            "file_suffix":
                "Tables",

            "entries":
                table_entries,

            "plsql":
                False
        })


    # =====================================================
    # 3 - INSERTS
    # =====================================================

    insert_entries = []


    for index, insert in enumerate(
        metadata.get(
            "inserts",
            []
        ),
        start=1
    ):

        target_table = (
            insert.get(
                "target_table",
                ""
            )
        )


        insert_entries.append({

            "object_name":
                (
                    f"{target_table} "
                    f"#{index}"
                ),

            "object_type":
                "INSERT",

            "sql":
                insert.get(
                    "sql",
                    ""
                )
        })


    if insert_entries:

        groups.append({

            "type":
                "INSERT",

            "file_suffix":
                "Inserts",

            "entries":
                insert_entries,

            "plsql":
                False
        })


    # =====================================================
    # 4 - VIEWS
    # =====================================================

    view_entries = []


    for view in metadata.get(
        "views",
        []
    ):

        view_entries.append({

            "object_name":
                view.get(
                    "view_name",
                    ""
                ),

            "object_type":
                "VIEW",

            "sql":
                view.get(
                    "sql",
                    ""
                )
        })


    if view_entries:

        groups.append({

            "type":
                "VIEW",

            "file_suffix":
                "Views",

            "entries":
                view_entries,

            "plsql":
                False
        })


    # =====================================================
    # 5 - PACKAGE SPECS
    # =====================================================

    package_spec_entries = []


    for package in metadata.get(
        "packages",
        []
    ):

        package_spec = (
            package.get(
                "package_spec",
                ""
            )
        )


        if not package_spec:

            continue


        package_spec_entries.append({

            "object_name":
                package.get(
                    "package_name",
                    ""
                ),

            "object_type":
                "PACKAGE SPEC",

            "sql":
                package_spec
        })


    if package_spec_entries:

        groups.append({

            "type":
                "PACKAGE SPEC",

            "file_suffix":
                "Package_Specs",

            "entries":
                package_spec_entries,

            "plsql":
                True
        })


    # =====================================================
    # 6 - PACKAGE BODIES
    # =====================================================

    package_body_entries = []


    for package in metadata.get(
        "packages",
        []
    ):

        package_body = (
            package.get(
                "package_body",
                ""
            )
        )


        if not package_body:

            continue


        package_body_entries.append({

            "object_name":
                package.get(
                    "package_name",
                    ""
                ),

            "object_type":
                "PACKAGE BODY",

            "sql":
                package_body
        })


    if package_body_entries:

        groups.append({

            "type":
                "PACKAGE BODY",

            "file_suffix":
                "Package_Bodies",

            "entries":
                package_body_entries,

            "plsql":
                True
        })


    # =====================================================
    # 7 - INDEXES
    # =====================================================

    index_entries = []


    for index in metadata.get(
        "indexes",
        []
    ):

        index_entries.append({

            "object_name":
                index.get(
                    "index_name",
                    ""
                ),

            "object_type":
                "INDEX",

            "sql":
                index.get(
                    "sql",
                    ""
                )
        })


    if index_entries:

        groups.append({

            "type":
                "INDEX",

            "file_suffix":
                "Indexes",

            "entries":
                index_entries,

            "plsql":
                False
        })


    # =====================================================
    # 8 - TRIGGERS
    # =====================================================

    trigger_entries = []


    for trigger in metadata.get(
        "triggers",
        []
    ):

        trigger_entries.append({

            "object_name":
                trigger.get(
                    "trigger_name",
                    ""
                ),

            "object_type":
                "TRIGGER",

            "sql":
                trigger.get(
                    "sql",
                    ""
                )
        })


    if trigger_entries:

        groups.append({

            "type":
                "TRIGGER",

            "file_suffix":
                "Triggers",

            "entries":
                trigger_entries,

            "plsql":
                True
        })


    # =====================================================
    # GENERATE ONLY NON EMPTY FILES
    # =====================================================

    current_order = 1


    for group in groups:

        entries = group[
            "entries"
        ]


        if not entries:

            continue


        file_name = (

            f"{current_order}_"
            f"{group['file_suffix']}.sql"
        )


        file_path = (
            write_consolidated_script(

                scripts_folder,

                file_name,

                entries,

                plsql=
                    group[
                        "plsql"
                    ]
            )
        )


        installation_scripts.append({

            "order":
                current_order,

            "type":
                group[
                    "type"
                ],

            "file_name":
                file_name,

            "file_path":
                file_path,

            "objects":
                [

                    entry.get(
                        "object_name",
                        ""
                    )

                    for entry in entries
                ]
        })


        current_order += 1


    return installation_scripts


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

    # =====================================================
    # CONSOLIDATED INSTALLATION SCRIPTS
    # =====================================================

    installation_scripts = (
        build_installation_scripts(

            metadata,

            folders[
                "scripts"
            ]
        )
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
            trigger_files,

        "scripts_folder":
            folders["scripts"],

        "installation_scripts":
            installation_scripts
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