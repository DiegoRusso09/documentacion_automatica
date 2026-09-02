# =========================================================
# FILE:
# oic_doc_generator/backend/parsers/sql_insert_parser.py
# =========================================================

import re


# =========================================================
# NORMALIZE OBJECT NAME
# =========================================================

def normalize_object_name(
    value
):

    if not value:

        return ""

    value = (
        str(value)
        .replace('"', '')
        .strip()
    )

    return (
        value
        .split(".")[-1]
        .upper()
    )


# =========================================================
# MASK TEXT PRESERVING POSITION
# =========================================================

def mask_text(
    value
):

    return "".join(

        "\n"
        if char == "\n"
        else " "

        for char in value
    )


# =========================================================
# MASK COMMENTS
# =========================================================

def mask_comments(
    sql_text
):

    pattern = re.compile(

        r"""
        --[^\r\n]*
        |
        /\*.*?\*/
        """,

        flags=
            re.MULTILINE
            |
            re.DOTALL
            |
            re.VERBOSE
    )

    return pattern.sub(
        lambda match:
            mask_text(
                match.group(0)
            ),
        sql_text
    )


# =========================================================
# MASK PL/SQL BLOCKS
# =========================================================
#
# Esto evita interpretar como scripts de carga los INSERT
# contenidos dentro de:
#
# - PACKAGE
# - PACKAGE BODY
# - TRIGGER
# - PROCEDURE
# - FUNCTION
# - bloques DECLARE / BEGIN
#
# =========================================================

def mask_plsql_blocks(
    sql_text
):

    result = sql_text


    create_block_pattern = re.compile(

        r"""
        ^\s*
        CREATE
        \s+
        (?:OR\s+REPLACE\s+)?
        (?:
            PACKAGE(?:\s+BODY)?
            |
            TRIGGER
            |
            PROCEDURE
            |
            FUNCTION
        )
        \b
        .*?
        ^\s*/\s*$
        """,

        flags=
            re.IGNORECASE
            |
            re.MULTILINE
            |
            re.DOTALL
            |
            re.VERBOSE
    )


    result = create_block_pattern.sub(

        lambda match:
            mask_text(
                match.group(0)
            ),

        result
    )


    anonymous_block_pattern = re.compile(

        r"""
        ^\s*
        (?:
            DECLARE
            |
            BEGIN
        )
        \b
        .*?
        ^\s*/\s*$
        """,

        flags=
            re.IGNORECASE
            |
            re.MULTILINE
            |
            re.DOTALL
            |
            re.VERBOSE
    )


    result = anonymous_block_pattern.sub(

        lambda match:
            mask_text(
                match.group(0)
            ),

        result
    )


    return result


# =========================================================
# FIND STATEMENT END
# =========================================================

def find_statement_end(
    sql_text,
    start_position
):

    position = start_position

    in_single_quote = False
    in_double_quote = False


    while position < len(
        sql_text
    ):

        char = sql_text[
            position
        ]


        # =================================================
        # SINGLE QUOTE
        # =================================================

        if char == "'" and not in_double_quote:

            if in_single_quote:

                if (
                    position + 1
                    <
                    len(sql_text)
                    and
                    sql_text[
                        position + 1
                    ] == "'"
                ):

                    position += 2
                    continue

            in_single_quote = (
                not in_single_quote
            )


        # =================================================
        # DOUBLE QUOTE
        # =================================================

        elif char == '"' and not in_single_quote:

            in_double_quote = (
                not in_double_quote
            )


        # =================================================
        # STATEMENT END
        # =================================================

        elif (

            char == ";"

            and

            not in_single_quote

            and

            not in_double_quote

        ):

            return (
                position + 1
            )


        position += 1


    return len(
        sql_text
    )


# =========================================================
# EXTRACT TARGET TABLES
# =========================================================
#
# También soporta:
#
# INSERT ALL
#     INTO TABLE_A ...
#     INTO TABLE_B ...
#
# =========================================================

def extract_target_tables(
    statement
):

    result = []


    matches = re.findall(

        r"""
        \bINTO
        \s+
        ([A-Z0-9_$#\."]+)
        """,

        statement,

        flags=
            re.IGNORECASE
            |
            re.VERBOSE
    )


    for value in matches:

        table_name = (
            normalize_object_name(
                value
            )
        )


        if (
            table_name
            and
            table_name not in result
        ):

            result.append(
                table_name
            )


    return result


# =========================================================
# EXTRACT REFERENCED TABLES
# =========================================================

def extract_referenced_tables(
    statement
):

    result = []


    matches = re.findall(

        r"""
        \b
        (?:
            FROM
            |
            JOIN
        )
        \s+
        ([A-Z0-9_$#\."]+)
        """,

        statement,

        flags=
            re.IGNORECASE
            |
            re.VERBOSE
    )


    for value in matches:

        table_name = (
            normalize_object_name(
                value
            )
        )


        if (
            table_name
            and
            table_name != "DUAL"
            and
            table_name not in result
        ):

            result.append(
                table_name
            )


    return result


# =========================================================
# EXTRACT REFERENCED SEQUENCES
# =========================================================

def extract_referenced_sequences(
    statement
):

    result = []


    matches = re.findall(

        r"""
        ([A-Z0-9_$#\."]+)
        \s*
        \.
        \s*
        NEXTVAL
        """,

        statement,

        flags=
            re.IGNORECASE
            |
            re.VERBOSE
    )


    for value in matches:

        sequence_name = (
            normalize_object_name(
                value
            )
        )


        if (
            sequence_name
            and
            sequence_name not in result
        ):

            result.append(
                sequence_name
            )


    return result


# =========================================================
# EXTRACT INSERTS
# =========================================================

def extract_inserts(
    sql_text
):

    result = []


    if not sql_text:

        return result


    # =====================================================
    # MASK CONTENT THAT MUST NOT BE CONSIDERED
    # =====================================================

    searchable_sql = (
        mask_comments(
            sql_text
        )
    )


    searchable_sql = (
        mask_plsql_blocks(
            searchable_sql
        )
    )


    # =====================================================
    # FIND TOP LEVEL INSERTS
    # =====================================================

    insert_pattern = re.compile(

        r"""
        \bINSERT
        \s+
        (?:
            ALL\s+
            |
            FIRST\s+
        )?
        INTO
        \b
        """,

        flags=
            re.IGNORECASE
            |
            re.VERBOSE
    )


    matches = list(
        insert_pattern.finditer(
            searchable_sql
        )
    )


    for index, match in enumerate(
        matches,
        start=1
    ):

        start_position = (
            match.start()
        )


        end_position = (
            find_statement_end(
                sql_text,
                start_position
            )
        )


        statement = (
            sql_text[
                start_position:
                end_position
            ]
            .strip()
        )


        if not statement:

            continue


        target_tables = (
            extract_target_tables(
                statement
            )
        )


        if not target_tables:

            continue


        result.append({

            "insert_order":
                index,

            "target_table":
                target_tables[0],

            "target_tables":
                target_tables,

            "referenced_tables":
                extract_referenced_tables(
                    statement
                ),

            "referenced_sequences":
                extract_referenced_sequences(
                    statement
                ),

            "sql":
                statement
        })


    return result