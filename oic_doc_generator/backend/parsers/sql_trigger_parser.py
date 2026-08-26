import re


# =========================================================
# EXTRACT TRIGGERS
# =========================================================

def extract_triggers(
    sql_text
):

    result = []


    pattern = re.compile(

        r"""
        CREATE
        \s+
        (?:OR\s+REPLACE\s+)?
        (?:EDITIONABLE\s+)?
        TRIGGER
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

        trigger_name = (
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


        trigger_sql = (
            sql_text[
                start_position:
                end_position
            ]
            .strip()
        )


        # =============================================
        # CORTAR ÚNICAMENTE POR "/" EN UNA LÍNEA
        # INDEPENDIENTE.
        #
        # NO por ";" porque el body PL/SQL los utiliza.
        # =============================================

        delimiter = re.search(

            r"""
            \n
            \s*
            /
            \s*
            (?=
                \n
                |
                \Z
            )
            """,

            trigger_sql,

            flags=
                re.VERBOSE
        )


        if delimiter:

            trigger_sql = (
                trigger_sql[
                    :
                    delimiter.start()
                ]
                .strip()
            )


        # =============================================
        # TABLA DEL TRIGGER
        # =============================================

        table_match = re.search(

            r"""
            \bON
            \s+
            "?([A-Z0-9_]+)"?
            """,

            trigger_sql,

            flags=
                re.IGNORECASE
                |
                re.VERBOSE
        )


        table_name = (

            table_match.group(1)

            if table_match

            else ""
        )


        # =============================================
        # EVENTOS
        # =============================================

        events = []


        for event in [
            "INSERT",
            "UPDATE",
            "DELETE"
        ]:

            if re.search(
                rf"\b{event}\b",
                trigger_sql,
                flags=re.IGNORECASE
            ):

                events.append(
                    event
                )


        result.append({

            "trigger_name":
                trigger_name,

            "table_name":
                table_name,

            "events":
                events,

            "description":
                "",

            "sql":
                trigger_sql
        })


    return result