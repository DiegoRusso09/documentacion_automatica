import re


# =========================================================
# EXTRACT INDEXES
# =========================================================

def extract_indexes(
    sql_text
):

    result = []

    pattern = re.compile(

        r"""
        CREATE
        \s+
        (UNIQUE\s+)?
        INDEX
        \s+
        ([A-Z0-9_\."]+)
        \s+
        ON
        \s+
        ([A-Z0-9_\."]+)
        """,

        flags=
            re.IGNORECASE
            |
            re.VERBOSE
    )


    matches = list(
        pattern.finditer(
            sql_text
        )
    )


    for index, match in enumerate(
        matches
    ):

        index_type = (
            "UNIQUE"
            if match.group(1)
            else "NORMAL"
        )


        index_name = (
            match.group(2)
            .replace('"', '')
            .split(".")[-1]
            .strip()
        )


        table_name = (
            match.group(3)
            .replace('"', '')
            .split(".")[-1]
            .strip()
        )


        start_position = (
            match.start()
        )


        if index + 1 < len(matches):

            end_position = (
                matches[
                    index + 1
                ].start()
            )

        else:

            end_position = (
                len(sql_text)
            )


        index_sql = (
            sql_text[
                start_position:
                end_position
            ]
            .strip()
        )


        delimiter = re.search(

            r"""
            \n
            \s*
            (?:
                /
                |
                -{20,}
            )
            """,

            index_sql,

            flags=
                re.VERBOSE
        )


        if delimiter:

            index_sql = (
                index_sql[
                    :
                    delimiter.start()
                ]
                .strip()
            )


        result.append({

            "index_name":
                index_name,

            "table_name":
                table_name,

            "index_type":
                index_type,

            "description":
                "",

            "sql":
                index_sql
        })


    return result