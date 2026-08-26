# =========================================================
# FILE:
# oic_doc_generator/backend/parsers/sql_view_parser.py
# =========================================================

import re


# =========================================================
# PARSE VIEW
# =========================================================

def parse_view(
    view_name,
    view_sql
):

    return {

        "view_name":
            view_name,

        "description":
            "",

        "sql":
            view_sql.strip()
    }


# =========================================================
# EXTRACT VIEWS
# =========================================================

def extract_views(
    sql_text
):

    result = []


    # =====================================================
    # DETECTAR INICIO DE CADA VIEW
    #
    # Soporta ejemplos como:
    #
    # CREATE VIEW ...
    # CREATE OR REPLACE VIEW ...
    # CREATE OR REPLACE FORCE VIEW ...
    # CREATE OR REPLACE FORCE EDITIONABLE VIEW ...
    # =====================================================

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


    # =====================================================
    # RECORRER VISTAS
    # =====================================================

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


        # =================================================
        # FINAL DEL BLOQUE
        #
        # Inicialmente tomamos como límite:
        # - siguiente CREATE VIEW
        # - fin del archivo
        # =================================================

        if (
            index + 1
            <
            len(matches)
        ):

            end_position = (
                matches[
                    index + 1
                ].start()
            )

        else:

            end_position = (
                len(
                    sql_text
                )
            )


        view_sql = (
            sql_text[
                start_position:
                end_position
            ]
            .strip()
        )


        # =================================================
        # SI EXISTE "/" COMO SEPARADOR ORACLE,
        # CORTAR ALLÍ.
        # =================================================

        separator = re.search(

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

            view_sql,

            flags=
                re.IGNORECASE
                |
                re.VERBOSE
        )


        if separator:

            view_sql = (
                view_sql[
                    :
                    separator.start()
                ]
                .strip()
            )


        result.append(

            parse_view(
                view_name,
                view_sql
            )
        )


    return result