# =========================================================
# FILE: parsers/integration_parser.py
# =========================================================

import os


# =========================================================
# FIND ICS PROPERTIES FILE
# =========================================================

def find_ics_properties_file(
    base_path
):

    for root, dirs, files in os.walk(
        base_path
    ):

        for file in files:

            if (
                file ==
                "ics_project_attributes.properties"
            ):

                return os.path.join(
                    root,
                    file
                )

    return None


# =========================================================
# READ PROPERTIES FILE
# =========================================================

def read_properties_file(
    properties_file
):

    result = {}

    if not properties_file:
        return result

    try:

        with open(

            properties_file,
            "r",
            encoding="utf-8",
            errors="ignore"

        ) as f:

            lines = f.readlines()

        for line in lines:

            line = line.strip()

            if not line:
                continue

            if "=" not in line:
                continue

            key, value = line.split(
                "=",
                1
            )

            result[
                key.strip()
            ] = value.strip()

    except:

        pass

    return result


# =========================================================
# GET INTEGRATION METADATA
# =========================================================

def get_integration_metadata(
    base_path
):

    properties_file = (
        find_ics_properties_file(
            base_path
        )
    )


    props = read_properties_file(
        properties_file
    )


    # =====================================================
    # INTEGRATION STYLE
    # =====================================================
    #
    # Algunos exports antiguos/nuevos no contienen:
    #
    # integrationStyle=...
    #
    # sino que Oracle guarda el estilo dentro de:
    #
    # smartTags=...,style\:scheduled orchestration
    #
    # o:
    #
    # smartTags=...,style\:app driven orchestration
    #
    # =====================================================

    integration_style = (
        props.get(
            "integrationStyle",
            ""
        )
        or
        ""
    ).strip()


    smart_tags = (
        props.get(
            "smartTags",
            ""
        )
        or
        ""
    ).strip()


    if (
        not integration_style
        and
        smart_tags
    ):

        normalized_tags = (
            smart_tags
            .replace(
                "\\:",
                ":"
            )
            .lower()
        )


        if (
            "style:scheduled orchestration"
            in
            normalized_tags
            or
            "style:scheduled"
            in
            normalized_tags
        ):

            integration_style = (
                "scheduled orchestration"
            )


        elif (
            "style:app driven orchestration"
            in
            normalized_tags
            or
            "style:app driven"
            in
            normalized_tags
        ):

            integration_style = (
                "app driven orchestration"
            )


    if not integration_style:

        integration_style = "UNKNOWN"


    # =====================================================
    # RESULT
    # =====================================================

    result = {

        "project_version":
            props.get(
                "project_version",
                "UNKNOWN"
            ),

        "project_persisted_state":
            props.get(
                "project_persisted_state",
                "UNKNOWN"
            ),

        "integration_style":
            integration_style,

        "project_code":
            props.get(
                "project_code",
                ""
            ),

        "project_name":
            props.get(
                "project_name",
                ""
            ),

        # Útiles para diagnóstico y futuras reglas.
        "smart_tags":
            smart_tags,

        "mep_type":
            props.get(
                "mep_type",
                ""
            )
    }


    return result


# =========================================================
# INTEGRATION IS ACTIVE
# =========================================================

def integration_is_active(
    metadata
):

    state = (

        metadata.get(
            "project_persisted_state",
            ""
        )

        .strip()
        .upper()

    )

    return (
        state == "ACTIVATED"
    )


# =========================================================
# IS SCHEDULED
# =========================================================

def integration_is_scheduled(
    metadata
):

    style = (

        metadata.get(
            "integration_style",
            ""
        )

        .strip()
        .lower()

    )

    return (
        "scheduled"
        in style
    )


# =========================================================
# IS APP DRIVEN
# =========================================================

def integration_is_app_driven(
    metadata
):

    style = (

        metadata.get(
            "integration_style",
            ""
        )

        .strip()
        .lower()

    )

    return (
        "app"
        in style
    )