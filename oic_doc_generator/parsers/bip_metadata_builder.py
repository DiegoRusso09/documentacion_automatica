# =========================================================
# FILE:
# oic_doc_generator/parsers/bip_metadata_builder.py
# =========================================================

from parsers.bip_archive_parser import (
    get_report_artifacts,
    get_datamodel_artifacts
)

from parsers.bip_relationship_parser import (
    match_reports_with_dms
)


# =========================================================
# BUILD BIP REPORT CATALOG
# =========================================================

def build_bip_report_catalog(
    artifact_tree
):

    result = {

        "reports": [],

        "warnings": []
    }

    if not artifact_tree:

        return result

    # =====================================================
    # REPORTS
    # =====================================================

    report_artifacts = get_report_artifacts(
        artifact_tree
    )

    # =====================================================
    # DMS
    # =====================================================

    dm_artifacts = get_datamodel_artifacts(
        artifact_tree
    )

    # =====================================================
    # MATCH
    # =====================================================

    matched = match_reports_with_dms(

        report_artifacts,

        dm_artifacts
    )

    result["reports"] = matched.get(
        "reports",
        []
    )

    result["warnings"] = matched.get(
        "warnings",
        []
    )

    return result


# =========================================================
# BUILD BIP METADATA
# =========================================================

def build_bip_metadata(
    artifact_tree
):

    catalog = build_bip_report_catalog(
        artifact_tree
    )

    reports = catalog.get(
        "reports",
        []
    )

    result = []

    # =====================================================
    # ITERATE REPORTS
    # =====================================================

    for report in reports:

        # =================================================
        # GENERAL INFO
        # =================================================

        report_name = report.get(
            "report_name",
            ""
        )

        report_path = report.get(
            "report_path",
            ""
        )

        data_model = report.get(
            "data_model",
            ""
        )

        datasource = report.get(
            "datasource",
            ""
        )

        output_formats = report.get(
            "output_formats",
            []
        )

        template_files = report.get(
            "template_files",
            []
        )

        parameters = report.get(
            "parameters",
            []
        )

        dm_found = report.get(
            "dm_found",
            False
        )

        # =================================================
        # OUTPUT FORMAT STRING
        # =================================================

        output_format_string = ", ".join(
            output_formats
        )

        # =================================================
        # TEMPLATE FILE STRING
        # =================================================

        template_file_string = ", ".join(
            template_files
        )

        # =================================================
        # METADATA OBJECT
        # =================================================

        metadata = {

            "report_name":
                report_name,

            "report_path":
                report_path,

            "data_model":
                data_model,

            "datasource":
                datasource,

            "output_formats":
                output_formats,

            "output_format_string":
                output_format_string,

            "template_files":
                template_files,

            "template_file_string":
                template_file_string,

            "parameters":
                parameters,

            "dm_found":
                dm_found,

            "frequency":
                "No aplica",

            "templates":
                report.get(
                    "templates",
                    []
                )
        }

        result.append(
            metadata
        )

    return {

        "reports":
            result,

        "warnings":
            catalog.get(
                "warnings",
                []
            )
    }


# =========================================================
# BUILD REPORT SUMMARY
# =========================================================

def build_report_summary(
    bip_metadata
):

    reports = bip_metadata.get(
        "reports",
        []
    )

    total_reports = len(
        reports
    )

    reports_with_dm = 0

    reports_without_dm = 0

    datasources = []

    output_formats = []

    # =====================================================
    # ITERATE
    # =====================================================

    for report in reports:

        if report.get(
            "dm_found",
            False
        ):

            reports_with_dm += 1

        else:

            reports_without_dm += 1

        datasource = report.get(
            "datasource",
            ""
        )

        if (

            datasource

            and

            datasource not in datasources
        ):

            datasources.append(
                datasource
            )

        for output in report.get(
            "output_formats",
            []
        ):

            if output not in output_formats:

                output_formats.append(
                    output
                )

    return {

        "total_reports":
            total_reports,

        "reports_with_dm":
            reports_with_dm,

        "reports_without_dm":
            reports_without_dm,

        "datasources":
            datasources,

        "output_formats":
            output_formats
    }


# =========================================================
# GET REPORT BY NAME
# =========================================================

def get_report_by_name(
    bip_metadata,
    report_name
):

    reports = bip_metadata.get(
        "reports",
        []
    )

    for report in reports:

        if (

            report.get(
                "report_name",
                ""
            )

            ==

            report_name
        ):

            return report

    return None