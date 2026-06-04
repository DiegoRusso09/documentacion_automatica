# =========================================================
# FILE:
# oic_doc_generator/parsers/integration_metadata_parser.py
# =========================================================

import os


# =========================================================
# FIND ATTRIBUTES FILE
# =========================================================

def find_attributes_file(
    extracted_iar
):

    for root, dirs, files in os.walk(
        extracted_iar
    ):

        for file in files:

            if (
                file
                ==
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
    file_path
):

    result = {}

    if not file_path:

        return result

    if not os.path.exists(
        file_path
    ):

        return result

    try:

        with open(

            file_path,

            "r",

            encoding="utf-8"
        ) as file:

            lines = file.readlines()

    except:

        return result

    # =====================================================
    # ITERATE LINES
    # =====================================================

    for line in lines:

        line = line.strip()

        if not line:

            continue

        if "=" not in line:

            continue

        parts = line.split(
            "=",
            1
        )

        key = parts[0].strip()

        value = parts[1].strip()

        result[key] = value

    return result


# =========================================================
# GET INTEGRATION METADATA
# =========================================================

def get_integration_metadata(
    extracted_iar
):

    attributes_file = find_attributes_file(
        extracted_iar
    )

    properties = read_properties_file(
        attributes_file
    )

    integration_name = properties.get(
        "project_code",
        "Unknown Integration"
    )

    version = properties.get(
        "project_version",
        "01.00.0000"
    )

    state = properties.get(
        "project_persisted_state",
        "CONFIGURED"
    )

    pattern = properties.get(
        "project_integration_pattern",
        ""
    )

    schedule_enabled = properties.get(
        "project_schedule_applicable",
        "false"
    )

    # =====================================================
    # TYPE
    # =====================================================

    integration_type = "APP_DRIVEN"

    if (

        schedule_enabled.lower()
        ==
        "true"

        or

        "scheduled"
        in
        pattern.lower()
    ):

        integration_type = "SCHEDULED"

    # =====================================================
    # ACTIVE
    # =====================================================

    is_active = False

    if state.upper() in [

        "ACTIVATED",

        "ACTIVE"
    ]:

        is_active = True

    return {

        "name":
            integration_name,

        "version":
            version,

        "state":
            state,

        "type":
            integration_type,

        "is_active":
            is_active
    }


# =========================================================
# IS ACTIVE INTEGRATION
# =========================================================

def is_active_integration(
    extracted_iar
):

    metadata = get_integration_metadata(
        extracted_iar
    )

    return metadata.get(
        "is_active",
        False
    )


# =========================================================
# IS SCHEDULED INTEGRATION
# =========================================================

def is_scheduled_integration_metadata(
    extracted_iar
):

    metadata = get_integration_metadata(
        extracted_iar
    )

    return (
        metadata.get("type")
        ==
        "SCHEDULED"
    )