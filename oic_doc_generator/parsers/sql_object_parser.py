# =========================================================
# FILE:
# oic_doc_generator/parsers/sql_object_parser.py
# =========================================================

from oic_doc_generator.parsers.sql_table_parser import (
    extract_tables
)

from oic_doc_generator.parsers.sql_sequence_parser import (
    extract_sequences
)

from oic_doc_generator.parsers.sql_package_parser import (
    extract_packages
)


# =========================================================
# READ SQL FILE
# =========================================================

def read_sql_file(
    uploaded_file
):

    try:

        try:
            uploaded_file.seek(0)
        except:
            pass

        content = uploaded_file.read()

        if isinstance(
            content,
            bytes
        ):

            return content.decode(
                "utf-8",
                errors="ignore"
            )

        return str(
            content
        )

    except Exception:

        return ""


# =========================================================
# PARSE SINGLE FILE
# =========================================================

def parse_single_sql_file(
    uploaded_file
):

    result = {

        "tables": [],

        "sequences": [],

        "packages": []
    }

    sql_text = read_sql_file(
        uploaded_file
    )

    if not sql_text:

        return result

    # =====================================================
    # TABLES
    # =====================================================

    result["tables"] = extract_tables(
        sql_text
    )

    # =====================================================
    # SEQUENCES
    # =====================================================

    result["sequences"] = extract_sequences(
        sql_text
    )

    # =====================================================
    # PACKAGES
    # =====================================================

    result["packages"] = extract_packages(
        sql_text
    )

    return result


# =========================================================
# MERGE TABLES
# =========================================================

def merge_tables(
    all_tables
):

    result = {}

    for table in all_tables:

        table_name = str(
            table.get(
                "table_name",
                ""
            )
        ).upper()

        if not table_name:

            continue

        if table_name not in result:

            result[
                table_name
            ] = table

    return list(
        result.values()
    )


# =========================================================
# MERGE SEQUENCES
# =========================================================

def merge_sequences(
    all_sequences
):

    result = {}

    for sequence in all_sequences:

        sequence_name = str(
            sequence.get(
                "sequence_name",
                ""
            )
        ).upper()

        if not sequence_name:

            continue

        if sequence_name not in result:

            result[
                sequence_name
            ] = sequence

    return list(
        result.values()
    )


# =========================================================
# MERGE PACKAGES
# =========================================================

def merge_packages(
    all_packages
):

    result = {}

    for package in all_packages:

        package_name = str(
            package.get(
                "package_name",
                ""
            )
        ).upper()

        if not package_name:

            continue

        # =============================================
        # FIRST PACKAGE
        # =============================================

        if package_name not in result:

            result[
                package_name
            ] = {

                "package_name":
                    package.get(
                        "package_name",
                        package_name
                    ),

                "description":
                    "",

                "package_spec":
                    package.get(
                        "package_spec",
                        ""
                    ),

                "package_body":
                    package.get(
                        "package_body",
                        ""
                    ),

                "members":
                    package.get(
                        "members",
                        []
                    )
            }

            continue

        # =============================================
        # MERGE
        # =============================================

        current = result[
            package_name
        ]

        if (

            not current.get(
                "package_spec"
            )

            and

            package.get(
                "package_spec"
            )
        ):

            current[
                "package_spec"
            ] = package.get(
                "package_spec",
                ""
            )

        if (

            not current.get(
                "package_body"
            )

            and

            package.get(
                "package_body"
            )
        ):

            current[
                "package_body"
            ] = package.get(
                "package_body",
                ""
            )

        if (

            not current.get(
                "members"
            )

            and

            package.get(
                "members"
            )
        ):

            current[
                "members"
            ] = package.get(
                "members",
                []
            )

    return list(
        result.values()
    )

# =========================================================
# PARSE SQL FILES
# =========================================================

def parse_sql_files(
    uploaded_files
):

    result = {

        "tables": [],

        "sequences": [],

        "packages": [],

        "warnings": []
    }

    if not uploaded_files:

        return result

    all_tables = []

    all_sequences = []

    all_packages = []

    # =====================================================
    # ITERATE FILES
    # =====================================================

    for uploaded_file in uploaded_files:

        try:

            parsed = parse_single_sql_file(
                uploaded_file
            )

            all_tables.extend(
                parsed.get(
                    "tables",
                    []
                )
            )

            all_sequences.extend(
                parsed.get(
                    "sequences",
                    []
                )
            )

            all_packages.extend(
                parsed.get(
                    "packages",
                    []
                )
            )

        except Exception as e:

            file_name = getattr(
                uploaded_file,
                "name",
                "Archivo SQL"
            )

            result[
                "warnings"
            ].append(

                f"Error procesando "
                f"{file_name}: "
                f"{str(e)}"
            )

    # =====================================================
    # CONSOLIDATE
    # =====================================================

    result["tables"] = merge_tables(
        all_tables
    )

    result["sequences"] = merge_sequences(
        all_sequences
    )

    result["packages"] = merge_packages(
        all_packages
    )

    return result


# =========================================================
# GET PACKAGE MEMBERS
# =========================================================

def get_package_members(
    packages
):

    result = []

    for package in packages:

        package_name = package.get(
            "package_name",
            ""
        )

        members = package.get(
            "members",
            []
        )

        result.append({

            "package_name":
                package_name,

            "members":
                members
        })

    return result


# =========================================================
# BUILD DATABASE METADATA
# =========================================================

def build_database_metadata(
    uploaded_files
):

    sql_metadata = parse_sql_files(
        uploaded_files
    )

    return {

        "tables":
            sql_metadata.get(
                "tables",
                []
            ),

        "all_tables":
            sql_metadata.get(
                "tables",
                []
            ),

        "sequences":
            sql_metadata.get(
                "sequences",
                []
            ),

        "all_sequences":
            sql_metadata.get(
                "sequences",
                []
            ),

        "packages":
            sql_metadata.get(
                "packages",
                []
            ),

        "all_packages":
            sql_metadata.get(
                "packages",
                []
            ),

        "warnings":
            sql_metadata.get(
                "warnings",
                []
            )
    }