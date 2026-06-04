# =========================================================
# FILE:
# oic_doc_generator/parsers/sql_table_parser.py
# =========================================================

import re


# =========================================================
# SPLIT COLUMNS
# =========================================================

def split_columns(
    table_body
):

    result = []

    current = ""

    level = 0

    for char in table_body:

        if char == "(":
            level += 1

        elif char == ")":
            level -= 1

        if char == "," and level == 0:

            result.append(
                current.strip()
            )

            current = ""

            continue

        current += char

    if current.strip():

        result.append(
            current.strip()
        )

    return result


# =========================================================
# EXTRACT COLUMN
# =========================================================

def extract_column(
    line
):

    line = line.strip()

    if not line:

        return None

    upper = line.upper()

    if upper.startswith("CONSTRAINT"):

        return None

    if upper.startswith("PRIMARY KEY"):

        return None

    if upper.startswith("FOREIGN KEY"):

        return None

    match = re.match(

        r'^"?([A-Z0-9_]+)"?\s+([A-Z0-9]+)(\((.*?)\))?',

        line,

        flags=re.IGNORECASE
    )

    if not match:

        return None

    column_name = match.group(1)

    data_type = match.group(2)

    size = match.group(4) or ""

    return {

        "column_name":
            column_name,

        "data_type":
            data_type,

        "size":
            size,

        "description":
            ""
    }


# =========================================================
# EXTRACT PK
# =========================================================

def extract_primary_keys(
    table_body
):

    result = []

    matches = re.findall(

        r'PRIMARY\s+KEY\s*\((.*?)\)',

        table_body,

        flags=re.IGNORECASE | re.DOTALL
    )

    for match in matches:

        columns = match.split(",")

        for col in columns:

            result.append(
                col.strip().upper()
            )

    return result


# =========================================================
# EXTRACT FK
# =========================================================

def extract_foreign_keys(
    table_body
):

    result = []

    matches = re.findall(

        r'FOREIGN\s+KEY\s*\((.*?)\)\s*REFERENCES\s+([A-Z0-9_]+)\s*\((.*?)\)',

        table_body,

        flags=re.IGNORECASE | re.DOTALL
    )

    for match in matches:

        local_column = match[0].strip().upper()

        parent_table = match[1].strip()

        parent_column = match[2].strip()

        result.append({

            "column":
                local_column,

            "referenced_table":
                parent_table,

            "referenced_column":
                parent_column
        })

    return result


# =========================================================
# PARSE CREATE TABLE
# =========================================================

def parse_create_table(
    table_name,
    table_body,
    full_sql
):

    columns = []

    lines = split_columns(
        table_body
    )

    for line in lines:

        column = extract_column(
            line
        )

        if column:

            columns.append(
                column
            )

    return {

        "table_name":
            table_name,

        "columns":
            columns,

        "primary_keys":
            extract_primary_keys(
                table_body
            ),

        "foreign_keys":
            extract_foreign_keys(
                table_body
            ),

        "sql":
            full_sql
    }


# =========================================================
# EXTRACT TABLES
# =========================================================

def extract_tables(
    sql_text
):

    result = []

    pattern = re.compile(

        r'CREATE\s+TABLE\s+([A-Z0-9_\."]+)\s*\((.*?)\)\s*;',

        flags=re.IGNORECASE | re.DOTALL
    )

    matches = pattern.findall(
        sql_text
    )

    for match in matches:

        table_name = (
            match[0]
            .replace('"', '')
            .split(".")[-1]
            .strip()
        )

        table_body = match[1]

        full_sql = (

            f"CREATE TABLE "
            f"{table_name} "
            f"({table_body});"
        )

        result.append(

            parse_create_table(

                table_name,

                table_body,

                full_sql
            )
        )

    return result