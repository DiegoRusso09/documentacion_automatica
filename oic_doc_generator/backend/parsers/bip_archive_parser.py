# =========================================================
# FILE:
# oic_doc_generator/parsers/bip_archive_parser.py
# =========================================================

import os
import shutil
import tempfile
import zipfile
import uuid


# =========================================================
# SUPPORTED EXTENSIONS
# =========================================================

SUPPORTED_BIP_EXTENSIONS = [

    ".xdoz",

    ".xdmz",

    ".xdrz"
]


# =========================================================
# CREATE TEMP WORKSPACE
# =========================================================

def create_temp_bip_workspace():

    workspace = os.path.join(

        tempfile.gettempdir(),

        "bip_workspace_" + str(uuid.uuid4())
    )

    os.makedirs(
        workspace,
        exist_ok=True
    )

    return workspace


# =========================================================
# IS SUPPORTED BIP FILE
# =========================================================

def is_supported_bip_file(
    file_name
):

    lower = file_name.lower()

    for ext in SUPPORTED_BIP_EXTENSIONS:

        if lower.endswith(ext):

            return True

    return False


# =========================================================
# DETECT BIP ARTIFACT TYPE
# =========================================================

def detect_bip_artifact_type(
    file_path
):

    lower = file_path.lower()

    if lower.endswith(".xdoz"):

        return "report"

    if lower.endswith(".xdmz"):

        return "datamodel"

    if lower.endswith(".xdrz"):

        return "folder"

    return "unknown"


# =========================================================
# SAFE EXTRACT ZIP
# =========================================================

def safe_extract_zip(
    zip_path,
    extract_to
):

    try:

        with zipfile.ZipFile(
            zip_path,
            "r"
        ) as zip_ref:

            zip_ref.extractall(
                extract_to
            )

        return True

    except:

        return False


# =========================================================
# EXTRACT SINGLE ARTIFACT
# =========================================================

def extract_bip_artifact(
    file_path,
    workspace
):

    result = {

        "type":
            detect_bip_artifact_type(
                file_path
            ),

        "original_file":
            file_path,

        "workspace":
            "",

        "children":
            [],

        "valid":
            False
    }

    artifact_name = os.path.basename(
        file_path
    )

    unique_folder = (

        artifact_name.replace(
            ".",
            "_"
        )

        + "_"

        + str(uuid.uuid4())
    )

    artifact_workspace = os.path.join(

        workspace,

        unique_folder
    )

    os.makedirs(
        artifact_workspace,
        exist_ok=True
    )

    extracted_ok = safe_extract_zip(

        file_path,

        artifact_workspace
    )

    if not extracted_ok:

        return result

    result["workspace"] = artifact_workspace
    result["valid"] = True

    # =====================================================
    # RECURSIVE XDRZ
    # =====================================================

    if result["type"] == "folder":

        result["children"] = extract_xdrz_recursive(

            artifact_workspace,

            workspace
        )

    return result


# =========================================================
# EXTRACT XDRZ RECURSIVELY
# =========================================================

def extract_xdrz_recursive(
    root_folder,
    workspace
):

    result = []

    for root, dirs, files in os.walk(
        root_folder
    ):

        for file in files:

            if not is_supported_bip_file(
                file
            ):

                continue

            full_path = os.path.join(
                root,
                file
            )

            artifact = extract_bip_artifact(

                full_path,

                workspace
            )

            result.append(
                artifact
            )

    return result


# =========================================================
# BUILD BIP ARTIFACT TREE
# =========================================================

def build_bip_artifact_tree(
    uploaded_files
):

    workspace = create_temp_bip_workspace()

    result = {

        "workspace":
            workspace,

        "artifacts":
            [],

        "warnings":
            []
    }

    if not uploaded_files:

        return result

    # =====================================================
    # ITERATE FILES
    # =====================================================

    for uploaded_file in uploaded_files:

        try:

            # =============================================
            # STREAMLIT UploadedFile
            # =============================================

            if hasattr(
                uploaded_file,
                "name"
            ):

                original_name = uploaded_file.name

                temp_file_path = os.path.join(

                    workspace,

                    original_name
                )

                with open(
                    temp_file_path,
                    "wb"
                ) as f:

                    f.write(
                        uploaded_file.getbuffer()
                    )

                source_path = temp_file_path

            else:

                source_path = str(
                    uploaded_file
                )

                original_name = os.path.basename(
                    source_path
                )

            # =============================================
            # VALIDATE EXTENSION
            # =============================================

            if not is_supported_bip_file(
                original_name
            ):

                result["warnings"].append(

                    f"Archivo no soportado: "
                    f"{original_name}"
                )

                continue

            # =============================================
            # EXTRACT
            # =============================================

            artifact = extract_bip_artifact(

                source_path,

                workspace
            )

            if not artifact.get(
                "valid"
            ):

                result["warnings"].append(

                    f"No fue posible procesar: "
                    f"{original_name}"
                )

                continue

            result["artifacts"].append(
                artifact
            )

        except Exception as e:

            result["warnings"].append(

                f"Error procesando "
                f"{uploaded_file}: {str(e)}"
            )

    return result


# =========================================================
# FLATTEN ARTIFACTS
# =========================================================

def flatten_artifacts(
    artifacts
):

    result = []

    for artifact in artifacts:

        result.append(
            artifact
        )

        children = artifact.get(
            "children",
            []
        )

        if children:

            result.extend(

                flatten_artifacts(
                    children
                )
            )

    return result


# =========================================================
# GET REPORT ARTIFACTS
# =========================================================

def get_report_artifacts(
    artifact_tree
):

    result = []

    artifacts = flatten_artifacts(

        artifact_tree.get(
            "artifacts",
            []
        )
    )

    for artifact in artifacts:

        if artifact.get(
            "type"
        ) == "report":

            result.append(
                artifact
            )

    return result


# =========================================================
# GET DATAMODEL ARTIFACTS
# =========================================================

def get_datamodel_artifacts(
    artifact_tree
):

    result = []

    artifacts = flatten_artifacts(

        artifact_tree.get(
            "artifacts",
            []
        )
    )

    for artifact in artifacts:

        if artifact.get(
            "type"
        ) == "datamodel":

            result.append(
                artifact
            )

    return result


# =========================================================
# CLEAN WORKSPACE
# =========================================================

def clean_bip_workspace(
    workspace
):

    if not workspace:

        return

    if not os.path.exists(
        workspace
    ):

        return

    try:

        shutil.rmtree(
            workspace
        )

    except:

        pass