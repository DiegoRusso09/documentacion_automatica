import re


# =========================================================
# EXTRACT VIEWS
# =========================================================

def extract_views(
    sql_text
):

    result = []

    pattern = re.compile(

        r"""
        CREATE
        \s+
        (?:OR\s+REPLACE\s+)?
        (?:FORCE\s+)?
        (?:EDITIONABLE\s+)?
        VIEW
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

        view_name = (
            match.group(1)
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


        view_sql = (
            sql_text[
                start_position:
                end_position
            ]
            .strip()
        )


        # =============================================
        # ELIMINAR SEPARADOR / Y COMENTARIOS
        # DEL SIGUIENTE DDL
        # =============================================

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

            view_sql,

            flags=
                re.VERBOSE
        )


        if delimiter:

            view_sql = (
                view_sql[
                    :
                    delimiter.start()
                ]
                .strip()
            )


        result.append({

            "view_name":
                view_name,

            "description":
                "",

            "sql":
                view_sql
        })


    return result