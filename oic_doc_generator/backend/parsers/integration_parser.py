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


    props = (
        read_properties_file(
            properties_file
        )
    )


    # =====================================================
    # SMART TAGS
    # =====================================================

    smart_tags = (
        props.get(
            "smartTags",
            ""
        )
        or
        ""
    )


    # En el .properties Oracle escapa ":" como "\:"
    smart_tags_normalized = (
        smart_tags.replace(
            "\\:",
            ":"
        )
    )


    # =====================================================
    # INTEGRATION STYLE
    # =====================================================

    integration_style = (
        props.get(
            "integrationStyle",
            ""
        )
        or
        ""
    ).strip()


    # Algunos exports no tienen integrationStyle,
    # pero sí contienen el style dentro de smartTags.

    if not integration_style:

        smart_tags_lower = (
            smart_tags_normalized.lower()
        )


        if (
            "style:scheduled orchestration"
            in smart_tags_lower
            or
            "style:scheduled"
            in smart_tags_lower
        ):

            integration_style = (
                "scheduled orchestration"
            )


        elif (
            "style:app driven orchestration"
            in smart_tags_lower
            or
            "style:app driven"
            in smart_tags_lower
        ):

            integration_style = (
                "app driven orchestration"
            )


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
            integration_style
            or
            "UNKNOWN",

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

        "smart_tags":
            smart_tags_normalized,

        "mep_type":
            props.get(
                "mep_type",
                ""
            ),

        "package_name":
            props.get(
                "package_name",
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