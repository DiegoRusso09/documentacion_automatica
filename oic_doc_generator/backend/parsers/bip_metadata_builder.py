# =========================================================
# FILE:
# oic_doc_generator/parsers/bip_metadata_builder.py
# =========================================================

from oic_doc_generator.backend.parsers.bip_archive_parser import (
    get_report_artifacts,
    get_datamodel_artifacts
)

from oic_doc_generator.backend.parsers.bip_relationship_parser import (
    match_reports_with_dms
)

from oic_doc_generator.backend.parsers.bip_dm_parser import (
    parse_bip_datamodel
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

    # =====================================================
    # DATA MODELS
    # =====================================================

    dm_artifacts = get_datamodel_artifacts(
        artifact_tree
    )


    data_models = []

    data_model_keys = set()


    for dm_artifact in dm_artifacts:

        workspace = dm_artifact.get(
            "workspace",
            ""
        )


        if not workspace:
            continue


        dm_metadata = parse_bip_datamodel(
            workspace
        )


        dm_name = (
            dm_metadata.get(
                "dm_name",
                ""
            )
            or
            ""
        ).strip()


        dm_path = (
            dm_metadata.get(
                "dm_path",
                ""
            )
            or
            ""
        ).strip()


        if not dm_name:
            continue

        # =====================================================
        # DUPLICATE CONTROL
        # =====================================================

        dm_key = (
            dm_name.upper(),
            dm_path.upper()
        )


        if dm_key in data_model_keys:
            continue


        data_model_keys.add(
            dm_key
        )


        data_models.append({

            "dm_name":
                dm_name,

            "dm_path":
                dm_path,

            "datasource":
                dm_metadata.get(
                    "datasource",
                    ""
                ),

            "parameters":
                dm_metadata.get(
                    "parameters",
                    []
                ),

            "dataset_sqls":
                dm_metadata.get(
                    "dataset_sqls",
                    []
                ),

            "xsd_structure":
                dm_metadata.get(
                    "xsd_structure",
                    {}
                )
        })

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

        dataset_sqls = report.get(
            "dataset_sqls",
            []
        )

        xsd_structure = report.get(
            "xsd_structure",
            {}
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

            "dataset_sqls":
                dataset_sqls,

            "xsd_structure":
                xsd_structure,

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

        "data_models":
            data_models,

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