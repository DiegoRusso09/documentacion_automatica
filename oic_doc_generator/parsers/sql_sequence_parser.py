# =========================================================
# FILE:
# oic_doc_generator/parsers/sql_sequence_parser.py
# =========================================================

import re


# =========================================================
# EXTRACT START WITH
# =========================================================

def extract_start_with(
    sequence_sql
):

    match = re.search(

        r"START\s+WITH\s+(\d+)",

        sequence_sql,

        flags=re.IGNORECASE
    )

    if not match:

        return "1"

    return match.group(1)


# =========================================================
# PARSE SEQUENCE
# =========================================================

def parse_sequence(
    sequence_name,
    sequence_sql
):

    return {

        "sequence_name":
            sequence_name,

        "start_with":
            extract_start_with(
                sequence_sql
            ),

        "description":
            "",

        "sql":
            sequence_sql.strip()
    }


# =========================================================
# EXTRACT SEQUENCES
# =========================================================

def extract_sequences(
    sql_text
):

    result = []

    pattern = re.compile(

        r"""
        CREATE
        \s+
        SEQUENCE
        \s+
        ([A-Z0-9_\."]+)
        (.*?)
        ;
        """,

        flags=
            re.IGNORECASE
            |
            re.DOTALL
            |
            re.VERBOSE
    )

    matches = pattern.finditer(
        sql_text
    )

    for match in matches:

        sequence_name = (
            match.group(1)
            .replace('"', '')
            .split(".")[-1]
            .strip()
        )

        full_sql = (
            "CREATE SEQUENCE "
            + match.group(1)
            + match.group(2)
            + ";"
        )

        result.append(

            parse_sequence(

                sequence_name,

                full_sql
            )
        )

    return result