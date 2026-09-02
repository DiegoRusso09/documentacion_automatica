# =========================================================
# FILE:
# oic_doc_generator/backend/utils/bip_installation_plan.py
# =========================================================

import os
from pathlib import Path


from oic_doc_generator.backend.parsers.bip_metadata_builder import (
    build_bip_metadata
)

from oic_doc_generator.backend.parsers.bip_report_parser import (
    parse_bip_report
)

from oic_doc_generator.backend.parsers.bip_dm_parser import (
    parse_bip_datamodel
)


# =========================================================
# PRIORITY
# =========================================================

BIP_INSTALLATION_PRIORITY = {

    "folder":
        1,

    "datamodel":
        2,

    "report":
        3
}


# =========================================================
# LABELS
# =========================================================

BIP_INSTALLATION_LABELS = {

    "folder":
        "Carpeta",

    "datamodel":
        "Data Model",

    "report":
        "Reporte"
}


# =========================================================
# SAFE STEM
# =========================================================

def safe_stem(
    value
):

    if not value:

        return ""

    return (
        Path(
            os.path.basename(
                str(value)
            )
        )
        .stem
        .strip()
    )


# =========================================================
# NORMALIZE CATALOG PATH
# =========================================================

def normalize_catalog_path(
    value
):

    if not value:

        return ""

    value = (
        str(value)
        .replace(
            "\\",
            "/"
        )
        .strip()
    )


    while "//" in value:

        value = value.replace(
            "//",
            "/"
        )


    if not value.startswith(
        "/"
    ):

        value = (
            "/"
            +
            value
        )


    return value.rstrip(
        "/"
    )


# =========================================================
# DISPLAY PATH
# =========================================================
#
# Oracle metadata normalmente devuelve:
#
# /Custom/Financials/Expenses
#
# Mientras que en el catálogo el usuario visualiza:
#
# /Shared Folders/Custom/Financials/Expenses
#
# NO modificamos la metadata original.
# Esto es únicamente para documentación.
#
# =========================================================

def get_display_catalog_path(
    catalog_path
):

    catalog_path = (
        normalize_catalog_path(
            catalog_path
        )
    )


    if not catalog_path:

        return ""


    lower_path = (
        catalog_path.lower()
    )


    if lower_path.startswith(
        "/shared folders"
    ):

        return catalog_path


    if (
        lower_path == "/custom"
        or
        lower_path.startswith(
            "/custom/"
        )
    ):

        return (
            "/Shared Folders"
            +
            catalog_path
        )


    return catalog_path


# =========================================================
# GET PARENT PATH
# =========================================================

def get_parent_catalog_path(
    catalog_path
):

    catalog_path = (
        normalize_catalog_path(
            catalog_path
        )
    )


    if not catalog_path:

        return ""


    parts = [

        part

        for part in catalog_path.split(
            "/"
        )

        if part
    ]


    if len(parts) <= 1:

        return "/"


    return (
        "/"
        +
        "/".join(
            parts[:-1]
        )
    )


# =========================================================
# GET LAST PATH SEGMENT
# =========================================================

def get_last_path_segment(
    catalog_path
):

    catalog_path = (
        normalize_catalog_path(
            catalog_path
        )
    )


    if not catalog_path:

        return ""


    parts = [

        part

        for part in catalog_path.split(
            "/"
        )

        if part
    ]


    if not parts:

        return ""


    # IMPORTANTE:
    # no cambiar mayúsculas, minúsculas ni tildes.

    return parts[-1]


# =========================================================
# NORMALIZE NAME FOR COMPARISON
# =========================================================

def normalize_name(
    value
):

    return (
        str(
            value
            or
            ""
        )
        .strip()
        .lower()
    )


# =========================================================
# FIND REPORT PATH
# =========================================================

def find_report_path(
    artifact_name,
    bip_metadata
):

    artifact_name_normalized = (
        normalize_name(
            safe_stem(
                artifact_name
            )
        )
    )


    for report in bip_metadata.get(
        "reports",
        []
    ):

        report_name = (
            normalize_name(
                report.get(
                    "report_name",
                    ""
                )
            )
        )


        if (
            report_name
            ==
            artifact_name_normalized
        ):

            return (
                normalize_catalog_path(
                    report.get(
                        "report_path",
                        ""
                    )
                )
            )


    return ""


# =========================================================
# FIND DATA MODEL PATH
# =========================================================

def find_datamodel_path(
    artifact_name,
    bip_metadata
):

    artifact_name_normalized = (
        normalize_name(
            safe_stem(
                artifact_name
            )
        )
    )


    for dm in bip_metadata.get(
        "data_models",
        []
    ):

        dm_name = (
            normalize_name(
                dm.get(
                    "dm_name",
                    ""
                )
            )
        )


        if (
            dm_name
            ==
            artifact_name_normalized
        ):

            return (
                normalize_catalog_path(
                    dm.get(
                        "dm_path",
                        ""
                    )
                )
            )


    return ""


# =========================================================
# BUILD FOLDER LOCAL METADATA
# =========================================================
#
# Analiza SOLO ese XDRZ y sus hijos.
#
# Esto evita mezclar rutas provenientes de otros XDRZ,
# XDOZ o XDMZ cargados en la misma ejecución.
#
# =========================================================

def build_folder_local_metadata(
    folder_artifact
):

    local_tree = {

        "workspace":
            "",

        "artifacts": [
            folder_artifact
        ],

        "warnings":
            []
    }


    return (
        build_bip_metadata(
            local_tree
        )
    )


# =========================================================
# GET FOLDER CANDIDATE PATHS
# =========================================================

def get_folder_candidate_paths(
    folder_artifact
):

    result = []


    local_metadata = (
        build_folder_local_metadata(
            folder_artifact
        )
    )


    # =====================================================
    # REPORT PATHS
    # =====================================================

    for report in local_metadata.get(
        "reports",
        []
    ):

        path = (
            normalize_catalog_path(
                report.get(
                    "report_path",
                    ""
                )
            )
        )


        if (
            path
            and
            path not in result
        ):

            result.append(
                path
            )


    # =====================================================
    # DATA MODEL PATHS
    # =====================================================

    for dm in local_metadata.get(
        "data_models",
        []
    ):

        path = (
            normalize_catalog_path(
                dm.get(
                    "dm_path",
                    ""
                )
            )
        )


        if (
            path
            and
            path not in result
        ):

            result.append(
                path
            )


    return result


# =========================================================
# FIND SEGMENT INDEX
# =========================================================

def find_segment_index(
    path_parts,
    folder_name
):

    folder_key = (
        normalize_name(
            folder_name
        )
    )


    for index, part in enumerate(
        path_parts
    ):

        if (
            normalize_name(
                part
            )
            ==
            folder_key
        ):

            return index


    return None


# =========================================================
# RESOLVE XDRZ CATALOG PATH
# =========================================================
#
# Ejemplo:
#
# Archivo:
#   Expenses.xdrz
#
# Hijo encontrado:
#   /Custom/Financials/Expenses/Data Models
#
# Resultado:
#   /Custom/Financials/Expenses
#
# El nombre real "Expenses" se conserva exactamente
# como aparece en la ruta.
#
# =========================================================

def resolve_xdrz_catalog_path(
    folder_artifact
):

    original_file = (
        folder_artifact.get(
            "original_file",
            ""
        )
        or
        ""
    )


    folder_name = (
        safe_stem(
            original_file
        )
    )


    if not folder_name:

        return ""


    candidate_paths = (
        get_folder_candidate_paths(
            folder_artifact
        )
    )


    for path in candidate_paths:

        parts = [

            part

            for part in path.split(
                "/"
            )

            if part
        ]


        folder_index = (
            find_segment_index(
                parts,
                folder_name
            )
        )


        if folder_index is None:

            continue


        resolved_parts = (
            parts[
                :folder_index + 1
            ]
        )


        return (
            "/"
            +
            "/".join(
                resolved_parts
            )
        )


    # =====================================================
    # NO GUESS
    # =====================================================
    #
    # Si no encontramos el nombre de la carpeta dentro
    # de las rutas reales de sus hijos, no inventamos
    # ninguna ruta.
    #
    # =====================================================

    return ""


# =========================================================
# RESOLVE ARTIFACT ROUTES
# =========================================================

def resolve_artifact_routes(
    artifact,
    bip_metadata
):

    artifact_type = (
        artifact.get(
            "type",
            ""
        )
    )


    workspace = (
        artifact.get(
            "workspace",
            ""
        )
        or
        ""
    )


    # =====================================================
    # REPORT
    # =====================================================

    if artifact_type == "report":

        report_metadata = (
            parse_bip_report(
                workspace
            )
        )


        catalog_path = (
            normalize_catalog_path(
                report_metadata.get(
                    "report_path",
                    ""
                )
            )
        )


        return {

            "object_catalog_path":
                catalog_path,

            "upload_catalog_path":
                catalog_path
        }


    # =====================================================
    # DATA MODEL
    # =====================================================

    if artifact_type == "datamodel":

        dm_metadata = (
            parse_bip_datamodel(
                workspace
            )
        )


        catalog_path = (
            normalize_catalog_path(
                dm_metadata.get(
                    "dm_path",
                    ""
                )
            )
        )


        return {

            "object_catalog_path":
                catalog_path,

            "upload_catalog_path":
                catalog_path
        }


    # =====================================================
    # FOLDER
    # =====================================================

    if artifact_type == "folder":

        folder_catalog_path = (
            resolve_xdrz_catalog_path(
                artifact
            )
        )


        upload_catalog_path = (
            get_parent_catalog_path(
                folder_catalog_path
            )
            if folder_catalog_path
            else
            ""
        )


        return {

            "object_catalog_path":
                folder_catalog_path,

            "upload_catalog_path":
                upload_catalog_path
        }


    return {

        "object_catalog_path":
            "",

        "upload_catalog_path":
            ""
    }

# =========================================================
# BUILD BIP INSTALLATION PLAN
# =========================================================

def build_bip_installation_plan(
    artifact_tree,
    bip_metadata
):

    result = {

        "items":
            [],

        "warnings":
            []
    }


    if not artifact_tree:

        return result


    # =====================================================
    # IMPORTANT:
    #
    # SOLO TOP LEVEL ARTIFACTS
    #
    # No usamos flatten_artifacts().
    #
    # Un XDRZ se instala como UN archivo.
    # Sus hijos no deben convertirse nuevamente en pasos
    # de instalación porque generaríamos duplicados.
    # =====================================================

    artifacts = (
        artifact_tree.get(
            "artifacts",
            []
        )
    )


    temporary_items = []


    for original_index, artifact in enumerate(
        artifacts
    ):

        artifact_type = (
            artifact.get(
                "type",
                ""
            )
        )


        if artifact_type not in (
            "folder",
            "datamodel",
            "report"
        ):

            continue


        original_file = (
            artifact.get(
                "original_file",
                ""
            )
            or
            ""
        )


        file_name = (
            os.path.basename(
                original_file
            )
        )


        object_name = (
            safe_stem(
                file_name
            )
        )


        routes = (
            resolve_artifact_routes(
                artifact,
                bip_metadata
            )
        )


        object_catalog_path = (
            routes.get(
                "object_catalog_path",
                ""
            )
        )


        upload_catalog_path = (
            routes.get(
                "upload_catalog_path",
                ""
            )
        )


        route_resolved = bool(
            upload_catalog_path
        )


        if not route_resolved:

            result[
                "warnings"
            ].append(

                (
                    "No fue posible determinar "
                    "automáticamente la ruta de "
                    f"instalación para {file_name}."
                )
            )


        temporary_items.append({

            "priority":
                BIP_INSTALLATION_PRIORITY[
                    artifact_type
                ],

            "original_index":
                original_index,

            "artifact_type":
                artifact_type,

            "type_label":
                BIP_INSTALLATION_LABELS[
                    artifact_type
                ],

            "object_name":
                object_name,

            "file_name":
                file_name,

            "package_path":
                (
                    "../OTBI/"
                    +
                    file_name
                ),

            "object_catalog_path":
                object_catalog_path,

            "upload_catalog_path":
                upload_catalog_path,

            "display_object_path":
                get_display_catalog_path(
                    object_catalog_path
                ),

            "display_upload_path":
                get_display_catalog_path(
                    upload_catalog_path
                ),

            "target_folder_name":
                get_last_path_segment(
                    upload_catalog_path
                ),

            "route_resolved":
                route_resolved
        })


    # =====================================================
    # SORT
    # =====================================================
    #
    # 1 Folder
    # 2 Data Model
    # 3 Report
    #
    # Dentro del mismo tipo:
    # orden original de carga.
    #
    # =====================================================

    temporary_items.sort(

        key=lambda item: (

            item[
                "priority"
            ],

            item[
                "original_index"
            ]
        )
    )


    # =====================================================
    # FINAL ORDER
    # =====================================================

    for order, item in enumerate(
        temporary_items,
        start=1
    ):

        item[
            "order"
        ] = order


        item.pop(
            "priority",
            None
        )


        item.pop(
            "original_index",
            None
        )


        result[
            "items"
        ].append(
            item
        )


    return result