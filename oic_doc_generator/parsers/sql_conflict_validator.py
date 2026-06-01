# =========================================================
# FILE:
# oic_doc_generator/parsers/sql_conflict_validator.py
# =========================================================


# =========================================================
# NORMALIZE COLUMN
# =========================================================

def normalize_column(
    column
):

    return {

        "column_name":
            str(
                column.get(
                    "column_name",
                    ""
                )
            ).upper(),

        "data_type":
            str(
                column.get(
                    "data_type",
                    ""
                )
            ).upper(),

        "size":
            str(
                column.get(
                    "size",
                    ""
                )
            ).upper()
    }


# =========================================================
# COMPARE TABLES
# =========================================================

def compare_tables(
    table_a,
    table_b
):

    columns_a = {}

    columns_b = {}

    for column in table_a.get(
        "columns",
        []
    ):

        normalized = normalize_column(
            column
        )

        columns_a[
            normalized[
                "column_name"
            ]
        ] = normalized

    for column in table_b.get(
        "columns",
        []
    ):

        normalized = normalize_column(
            column
        )

        columns_b[
            normalized[
                "column_name"
            ]
        ] = normalized

    # =====================================================
    # SAME NUMBER OF COLUMNS
    # =====================================================

    if set(columns_a.keys()) != set(
        columns_b.keys()
    ):

        return False

    # =====================================================
    # VALIDATE EACH COLUMN
    # =====================================================

    for column_name in columns_a:

        col_a = columns_a[
            column_name
        ]

        col_b = columns_b[
            column_name
        ]

        if (
            col_a["data_type"]
            !=
            col_b["data_type"]
        ):

            return False

        if (
            col_a["size"]
            !=
            col_b["size"]
        ):

            return False

    return True


# =========================================================
# VALIDATE TABLES
# =========================================================

def validate_tables(
    tables
):

    errors = []

    grouped = {}

    for table in tables:

        table_name = str(
            table.get(
                "table_name",
                ""
            )
        ).upper()

        if not table_name:

            continue

        grouped.setdefault(
            table_name,
            []
        ).append(
            table
        )

    for table_name, versions in grouped.items():

        if len(
            versions
        ) <= 1:

            continue

        base = versions[0]

        for other in versions[1:]:

            if not compare_tables(
                base,
                other
            ):

                errors.append(

                    f"Tabla conflictiva: "
                    f"{table_name}"
                )

    return errors


# =========================================================
# VALIDATE SEQUENCES
# =========================================================

def validate_sequences(
    sequences
):

    errors = []

    grouped = {}

    for sequence in sequences:

        name = str(
            sequence.get(
                "sequence_name",
                ""
            )
        ).upper()

        if not name:

            continue

        grouped.setdefault(
            name,
            []
        ).append(
            sequence
        )

    for name, versions in grouped.items():

        if len(
            versions
        ) <= 1:

            continue

        start_values = set()

        for sequence in versions:

            start_values.add(

                str(
                    sequence.get(
                        "start_with",
                        ""
                    )
                )
            )

        if len(
            start_values
        ) > 1:

            errors.append(

                f"Secuencia conflictiva: "
                f"{name}"
            )

    return errors


# =========================================================
# VALIDATE PACKAGES
# =========================================================

def validate_packages(
    packages
):

    errors = []

    grouped = {}

    for package in packages:

        package_name = str(
            package.get(
                "package_name",
                ""
            )
        ).upper()

        if not package_name:

            continue

        grouped.setdefault(
            package_name,
            []
        ).append(
            package
        )

    for package_name, versions in grouped.items():

        if len(
            versions
        ) <= 1:

            continue

        base = versions[0]

        for other in versions[1:]:

            spec_different = (

                base.get(
                    "package_spec",
                    ""
                ).strip()

                !=

                other.get(
                    "package_spec",
                    ""
                ).strip()
            )

            body_different = (

                base.get(
                    "package_body",
                    ""
                ).strip()

                !=

                other.get(
                    "package_body",
                    ""
                ).strip()
            )

            if spec_different or body_different:

                errors.append(

                    f"Package conflictivo: "
                    f"{package_name}"
                )

                break

    return errors

# =========================================================
# VALIDATE SQL OBJECTS
# =========================================================

def validate_sql_objects(
    sql_metadata
):

    errors = []

    errors.extend(

        validate_tables(

            sql_metadata.get(
                "all_tables",

                sql_metadata.get(
                    "tables",
                    []
                )
            )
        )
    )

    errors.extend(

        validate_sequences(

            sql_metadata.get(
                "all_sequences",

                sql_metadata.get(
                    "sequences",
                    []
                )
            )
        )
    )

    errors.extend(

        validate_packages(

            sql_metadata.get(
                "all_packages",

                sql_metadata.get(
                    "packages",
                    []
                )
            )
        )
    )

    return {

        "valid":
            len(errors) == 0,

        "errors":
            errors
    }