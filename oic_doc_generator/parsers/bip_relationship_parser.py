# =========================================================
# FILE:
# oic_doc_generator/parsers/bip_relationship_parser.py
# =========================================================

from parsers.bip_report_parser import (
    parse_bip_report
)

from parsers.bip_dm_parser import (
    parse_bip_datamodel
)

import os

# =========================================================
# BUILD DATAMODEL MAP
# =========================================================

def normalize_name(
    value
):

    if not value:

        return ""

    value = str(value)

    # =====================================================
    # LOWER
    # =====================================================

    value = value.lower()

    # =====================================================
    # REMOVE EXTENSIONS
    # =====================================================

    extensions = [

        ".xdm",

        ".xdmz",

        ".xdo",

        ".xdoz"
    ]

    for ext in extensions:

        if value.endswith(ext):

            value = value[
                : -len(ext)
            ]

    # =====================================================
    # NORMALIZE SPACES
    # =====================================================

    value = value.replace(
        "\n",
        " "
    )

    value = value.replace(
        "\r",
        " "
    )

    value = value.replace(
        "\t",
        " "
    )

    # =====================================================
    # COLLAPSE MULTIPLE SPACES
    # =====================================================

    value = " ".join(
        value.split()
    )

    return value.strip()

# =========================================================
# BUILD DATAMODEL MAP
# =========================================================

def build_datamodel_map(
    datamodel_artifacts
):

    result = {}

    for artifact in datamodel_artifacts:

        workspace = artifact.get(
            "workspace",
            ""
        )

        if not workspace:

            continue


        dm_metadata = parse_bip_datamodel(
            workspace
        )

        # =================================================
        # DM NAME FROM ORIGINAL FILE
        # =================================================

        original_file = artifact.get(
            "original_file",
            ""
        )

        dm_name = ""

        if original_file:

            dm_name = normalize_name(

                os.path.basename(
                    original_file
                )
            )

        # =================================================
        # FALLBACK TO METADATA
        # =================================================

        if not dm_name:

            dm_name = normalize_name(

                dm_metadata.get(
                    "dm_name",
                    ""
                )
            )
            


        if not dm_name:

            continue

        # =================================================
        # DIRECT NAME
        # =================================================

        result[
            dm_name
        ] = dm_metadata

        # =================================================
        # ORIGINAL FILE NAME
        # =================================================

        original_file = artifact.get(
            "original_file",
            ""
        )

        if original_file:

            original_name = normalize_name(

                os.path.basename(
                    original_file
                )
            )

            result[
                original_name
            ] = dm_metadata

        # =================================================
        # FALLBACK USING WORKSPACE
        # =================================================

        workspace_name = normalize_name(

            os.path.basename(
                workspace
            )
        )

        if workspace_name:

            result[
                workspace_name
            ] = dm_metadata

        # =================================================
        # PARENT FOLDER + NAME
        # =================================================

        parent_folder = ""

        if original_file:

            parent_folder = os.path.basename(

                os.path.dirname(
                    original_file
                )
            ).lower()

        composite_key = (
            f"{parent_folder}|{dm_name}"
        )

        result[
            composite_key
        ] = dm_metadata

    return result

# =========================================================
# RESOLVE DM FOR REPORT
# =========================================================

def resolve_dm_for_report(
    report_metadata,
    dm_map
):

    requested_dm = normalize_name(

        report_metadata.get(
            "data_model",
            ""
        )
    )

    if not requested_dm:

        return None

    # =====================================================
    # DIRECT MATCH
    # =====================================================

    if requested_dm in dm_map:

        return dm_map[
            requested_dm
        ]

    # =====================================================
    # TRY REPORT PARENT FOLDER
    # =====================================================

    report_path = report_metadata.get(
        "report_path",
        ""
    )

    parent_folder = ""

    if report_path:

        parts = report_path.split("/")

        if len(parts) >= 2:

            parent_folder = (
                parts[-2]
                .strip()
                .lower()
            )

    composite_key = (
        f"{parent_folder}|{requested_dm}"
    )

    if composite_key in dm_map:

        return dm_map[
            composite_key
        ]

    # =====================================================
    # COMMON DATA MODEL FOLDERS
    # =====================================================

    common_folders = [

        "data models",

        "data model",

        "modelo de datos"
    ]

    for folder in common_folders:

        composite_key = (
            f"{folder}|{requested_dm}"
        )

        if composite_key in dm_map:

            return dm_map[
                composite_key
            ]

    return None


# =========================================================
# MATCH REPORTS WITH DMS
# =========================================================

def match_reports_with_dms(
    report_artifacts,
    datamodel_artifacts
):

    result = []

    warnings = []

    # =====================================================
    # BUILD DM MAP
    # =====================================================

    dm_map = build_datamodel_map(
        datamodel_artifacts
    )

    # =====================================================
    # ITERATE REPORTS
    # =====================================================

    for report_artifact in report_artifacts:

        workspace = report_artifact.get(
            "workspace",
            ""
        )

        if not workspace:

            continue

        # =================================================
        # REPORT METADATA
        # =================================================

        report_metadata = parse_bip_report(
            workspace
        )

        # =================================================
        # MATCH DM
        # =================================================

        matched_dm = resolve_dm_for_report(

            report_metadata,

            dm_map
        )

        # =================================================
        # WARNING
        # =================================================

        if not matched_dm:

            warnings.append(

                f"No se encontró el "
                f"Data Model para el "
                f"reporte "
                f"{report_metadata.get('report_name','')}"
            )

        # =================================================
        # CONSOLIDATED
        # =================================================

        consolidated = {

            "report_name":
                report_metadata.get(
                    "report_name",
                    ""
                ),

            "report_path":
                report_metadata.get(
                    "report_path",
                    ""
                ),

            "data_model":
                report_metadata.get(
                    "data_model",
                    ""
                ),

            "datasource":
                "",

            "templates":
                report_metadata.get(
                    "templates",
                    []
                ),

            "output_formats":
                report_metadata.get(
                    "output_formats",
                    []
                ),

            "template_files":
                report_metadata.get(
                    "template_files",
                    []
                ),

            "parameters":
                [],

            "dm_parameters":
                [],

            "dataset_sqls":
                [],

            "xsd_structure":
                {},

            "dm_found":
                matched_dm is not None,

            "dm_metadata":
                matched_dm
        }

        # =================================================
        # DATASOURCE
        # =================================================

        if matched_dm:

            consolidated[
                "datasource"
            ] = matched_dm.get(
                "datasource",
                ""
            )

        # =============================================
        # PARAMETERS
        # =============================================

        consolidated[
            "parameters"
        ] = matched_dm.get(
            "parameters",
            []
        )

        # =============================================
        # DATASET SQLS
        # =============================================

        consolidated[
            "dataset_sqls"
        ] = matched_dm.get(
            "dataset_sqls",
            []
        )

        # =============================================
        # XSD STRUCTURE
        # =============================================

        consolidated[
            "xsd_structure"
        ] = matched_dm.get(
            "xsd_structure",
            {}
        )

        result.append(
            consolidated
        )

    return {

        "reports":
            result,

        "warnings":
            warnings
    }


# =========================================================
# BUILD REPORT DEPENDENCY MAP
# =========================================================

def build_report_dependency_map(
    matched_reports
):

    result = {}

    reports = matched_reports.get(
        "reports",
        []
    )

    for report in reports:

        report_name = report.get(
            "report_name",
            ""
        )

        if not report_name:

            continue

        result[
            report_name
        ] = {

            "data_model":
                report.get(
                    "data_model",
                    ""
                ),

            "datasource":
                report.get(
                    "datasource",
                    ""
                ),

            "dm_found":
                report.get(
                    "dm_found",
                    False
                )
        }

    return result