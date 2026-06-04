import os
import shutil
import tempfile
import subprocess


# =========================================================
# BUILD MERMAID ERD
# =========================================================

def build_mermaid_erd_code(
    tables
):

    lines = [

        "erDiagram"
    ]

    # =====================================================
    # TABLE DEFINITIONS
    # =====================================================

    for table in tables:

        table_name = table.get(
            "table_name",
            ""
        )

        if not table_name:

            continue

        pk_columns = set(

            table.get(
                "primary_keys",
                []
            )
        )

        fk_columns = set(

            fk.get(
                "column",
                ""
            )

            for fk in table.get(
                "foreign_keys",
                []
            )
        )

        lines.append(
            f"{table_name} {{"
        )

        for column in table.get(
            "columns",
            []
        ):

            column_name = column.get(
                "column_name",
                ""
            )

            data_type = column.get(
                "data_type",
                "VARCHAR2"
            )

            tags = []

            if column_name in pk_columns:

                tags.append(
                    "PK"
                )

            if column_name in fk_columns:

                tags.append(
                    "FK"
                )

            suffix = ""

            if tags:

                suffix = " " + " ".join(tags)

            lines.append(

                f"    {data_type} "
                f"{column_name}"
                f"{suffix}"
            )

        lines.append(
            "}"
        )

        lines.append("")

    # =====================================================
    # RELATIONSHIPS
    # =====================================================

    for table in tables:

        child_table = table.get(
            "table_name",
            ""
        )

        for fk in table.get(
            "foreign_keys",
            []
        ):

            parent_table = fk.get(
                "referenced_table",
                ""
            )

            column_name = fk.get(
                "column",
                ""
            )

            if not parent_table:

                continue

            lines.append(

                f"{parent_table} "
                f"||--o{{ "
                f"{child_table} "
                f": {column_name}"
            )

    return "\n".join(
        lines
    )


# =========================================================
# GENERATE PNG
# =========================================================

def generate_erd_diagram(
    tables
):

    if not tables:

        return None

    mmdc_path = shutil.which(
        "mmdc"
    )

    if not mmdc_path:

        possible_paths = [

            r"C:\Users\LP-KQ-NEORA\AppData\Roaming\npm\mmdc.cmd",

            r"C:\Users\LP-KQ-NEORA\AppData\Roaming\npm\mmdc"
        ]

        for path in possible_paths:

            if os.path.exists(path):

                mmdc_path = path

                break

    if not mmdc_path:

        raise Exception(
            "No se encontró Mermaid CLI"
        )

    temp_dir = tempfile.mkdtemp()

    mmd_file = os.path.join(
        temp_dir,
        "erd.mmd"
    )

    png_file = os.path.join(
        temp_dir,
        "erd.png"
    )

    mermaid_code = (
        build_mermaid_erd_code(
            tables
        )
    )

    with open(

        mmd_file,

        "w",

        encoding="utf-8"

    ) as file:

        file.write(
            mermaid_code
        )

    result = subprocess.run(

        [
            mmdc_path,
            "-i",
            mmd_file,
            "-o",
            png_file,
            "-t",
            "neutral",
            "-b",
            "white",
            "-s",
            "2"
        ],

        capture_output=True,

        text=True
    )

    if result.returncode != 0:

        raise Exception(
            result.stderr
        )

    return png_file