# =========================================================
# FILE:
# oic_doc_generator/parsers/sql_package_parser.py
# =========================================================

import re


# =========================================================
# EXTRACT PACKAGE MEMBERS
# =========================================================

def extract_package_members(
    package_spec
):

    result = []

    # =====================================================
    # PROCEDURES
    # =====================================================

    procedure_matches = re.finditer(

        r"""
        PROCEDURE
        \s+
        ([A-Z0-9_]+)
        """,

        package_spec,

        flags=
            re.IGNORECASE
            |
            re.VERBOSE
    )

    for match in procedure_matches:

        result.append({

            "name":
                match.group(1),

            "type":
                "Procedimiento",

            "description":
                ""
        })

    # =====================================================
    # FUNCTIONS
    # =====================================================

    function_matches = re.finditer(

        r"""
        FUNCTION
        \s+
        ([A-Z0-9_]+)
        """,

        package_spec,

        flags=
            re.IGNORECASE
            |
            re.VERBOSE
    )

    for match in function_matches:

        result.append({

            "name":
                match.group(1),

            "type":
                "Función",

            "description":
                ""
        })

    return result


# =========================================================
# EXTRACT PACKAGE SPECS
# =========================================================

def extract_package_specs(
    sql_text
):

    result = {}

    pattern = re.compile(

        r"""
        CREATE
        \s+
        (?:OR\s+REPLACE\s+)?

        (?:
            NONEDITIONABLE
            \s+
        )?

        (?:
            EDITIONABLE
            \s+
        )?

        PACKAGE
        \s+
        ([A-Z0-9_\."]+)
        \s+
        (?:IS|AS)

        (.*?)

        END
        \s*
        (?:[A-Z0-9_"]+)?
        \s*
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

        package_name = (
            match.group(1)
            .replace('"', '')
            .split(".")[-1]
            .strip()
        )

        full_spec = match.group(0)

        result[
            package_name.upper()
        ] = {

            "package_name":
                package_name,

            "package_spec":
                full_spec,

            "members":
                extract_package_members(
                    full_spec
                )
        }

    return result


# =========================================================
# EXTRACT PACKAGE BODIES
# =========================================================

def extract_package_bodies(
    sql_text
):

    result = {}

    pattern = re.compile(

        r"""
        CREATE
        \s+
        (?:OR\s+REPLACE\s+)?

        (?:
            NONEDITIONABLE
            \s+
        )?

        (?:
            EDITIONABLE
            \s+
        )?

        PACKAGE
        \s+
        BODY
        \s+
        ([A-Z0-9_\."]+)
        \s+
        (?:IS|AS)

        (.*?)

        END
        \s*
        (?:[A-Z0-9_"]+)?
        \s*
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

        package_name = (
            match.group(1)
            .replace('"', '')
            .split(".")[-1]
            .strip()
        )

        result[
            package_name.upper()
        ] = match.group(0)

    return result


# =========================================================
# EXTRACT PACKAGES
# =========================================================

def extract_packages(
    sql_text
):

    result = []

    specs = extract_package_specs(
        sql_text
    )

    bodies = extract_package_bodies(
        sql_text
    )

    package_names = set()

    package_names.update(
        specs.keys()
    )

    package_names.update(
        bodies.keys()
    )

    for package_name in sorted(
        package_names
    ):

        spec_data = specs.get(
            package_name,
            {}
        )

        result.append({

            "package_name":
                spec_data.get(
                    "package_name",
                    package_name
                ),

            "description":
                "",

            "package_spec":
                spec_data.get(
                    "package_spec",
                    ""
                ),

            "package_body":
                bodies.get(
                    package_name,
                    ""
                ),

            "members":
                spec_data.get(
                    "members",
                    []
                )
        })

    return result
