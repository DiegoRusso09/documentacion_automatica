# =========================================================
# FILE:
# oic_doc_generator/parsers/bip_dm_parser.py
# =========================================================

import os
import xml.etree.ElementTree as ET

from utils.xml_utils import (
    clean_tag
)


# =========================================================
# FIND FILE RECURSIVE
# =========================================================

def find_file_recursive(
    root_folder,
    target_file
):

    for root, dirs, files in os.walk(
        root_folder
    ):

        for file in files:

            if file.lower() == target_file.lower():

                return os.path.join(
                    root,
                    file
                )

    return None


# =========================================================
# SAFE XML PARSE
# =========================================================

def safe_xml_parse(
    xml_path
):

    if not xml_path:

        return None

    if not os.path.exists(
        xml_path
    ):

        return None

    try:

        tree = ET.parse(
            xml_path
        )

        return tree.getroot()

    except:

        return None


# =========================================================
# EXTRACT DATASOURCE
# =========================================================

def extract_datasource(
    dm_root
):

    if dm_root is None:

        return ""

    # =====================================================
    # SEARCH ANY TAG WITH dataSourceRef
    # =====================================================

    for elem in dm_root.iter():

        datasource = elem.attrib.get(
            "dataSourceRef",
            ""
        )

        if datasource:

            return datasource

    return ""


# =========================================================
# EXTRACT SQL QUERIES
# =========================================================

def extract_sql_queries(
    dm_root
):

    result = []

    if dm_root is None:

        return result

    for elem in dm_root.iter():

        try:

            tag = clean_tag(
                elem.tag
            )

        except:

            continue

        # =================================================
        # SQL TAG
        # =================================================

        if tag.lower() != "sql":

            continue

        sql_text = ""

        if elem.text:

            sql_text = elem.text.strip()

        if sql_text:

            result.append(
                sql_text
            )

    return result


# =========================================================
# EXTRACT DATASETS
# =========================================================

def extract_datasets(
    dm_root
):

    result = []

    if dm_root is None:

        return result

    for elem in dm_root.iter():

        try:

            tag = clean_tag(
                elem.tag
            )

        except:

            continue

        # =================================================
        # DATASET
        # =================================================

        if tag.lower() not in [

            "sql",

            "dataquery",

            "query"
        ]:

            continue

        dataset_name = elem.attrib.get(
            "name",
            ""
        )

        datasource = elem.attrib.get(
            "dataSourceRef",
            ""
        )

        result.append({

            "name":
                dataset_name,

            "datasource":
                datasource
        })

    return result


# =========================================================
# EXTRACT DM PARAMETERS
# =========================================================

def extract_dm_parameters(
    dm_root
):

    result = []

    if dm_root is None:

        return result

    for elem in dm_root.iter():

        try:

            tag = clean_tag(
                elem.tag
            )

        except:

            continue

        # =================================================
        # PARAMETER
        # =================================================

        if tag.lower() != "parameter":

            continue

        parameter_name = elem.attrib.get(
            "name",
            ""
        )

        mandatory = elem.attrib.get(
            "mandatory",
            "false"
        )

        mandatory_text = (

            "Si"

            if mandatory.lower() == "true"

            else "No"
        )

        label = ""

        # =================================================
        # INPUT LABEL
        # =================================================

        for child in elem.iter():

            try:

                child_tag = clean_tag(
                    child.tag
                )

            except:

                continue

            if child_tag.lower() != "input":

                continue

            label = child.attrib.get(
                "label",
                ""
            )

            break

        # =================================================
        # FALLBACK LABEL
        # =================================================

        if not label:

            label = parameter_name

        result.append({

            "name":
                label,

            "code":
                parameter_name,

            "mandatory":
                mandatory_text,

            "description":
                ""
        })

    return result

# =========================================================
# EXTRACT DM NAME
# =========================================================

def extract_dm_name(
    dm_workspace
):

    if not dm_workspace:

        return ""

    # =====================================================
    # FIRST TRY:
    # REAL XDM FILE
    # =====================================================

    for root, dirs, files in os.walk(
        dm_workspace
    ):

        for file in files:

            lower = file.lower()

            if not lower.endswith(
                ".xdm"
            ):

                continue

            # =============================================
            # IGNORE INTERNAL FILE
            # =============================================

            if lower == "_datamodel.xdm":

                continue

            return os.path.splitext(
                file
            )[0].strip()

    # =====================================================
    # FALLBACK:
    # USE WORKSPACE NAME
    # =====================================================

    workspace_name = os.path.basename(
        dm_workspace
    )

    # =============================================
    # REMOVE RANDOM SUFFIX
    # =============================================

    if "_xdmz_" in workspace_name.lower():

        workspace_name = workspace_name.split(
            "_xdmz_"
        )[0]

    workspace_name = workspace_name.replace(
        "_",
        " "
    )

    workspace_name = workspace_name.replace(
        ".xdmz",
        ""
    )

    return workspace_name.strip()

# =========================================================
# PARSE BIP DATAMODEL
# =========================================================

def parse_bip_datamodel(
    dm_workspace
):

    result = {

        "dm_name": "",

        "datasource": "",

        "sql_queries": [],

        "datasets": [],

        "parameters": [],

        "dm_xml_path": ""
    }

    if not dm_workspace:

        return result

    # =====================================================
    # FIND DM XML
    # =====================================================

    dm_xml = find_file_recursive(

        dm_workspace,

        "_datamodel.xdm"
    )

    result["dm_xml_path"] = dm_xml

    if not dm_xml:

        return result

    # =====================================================
    # PARSE XML
    # =====================================================

    dm_root = safe_xml_parse(
        dm_xml
    )

    if dm_root is None:

        return result

    # =====================================================
    # DM NAME
    # =====================================================

    result["dm_name"] = extract_dm_name(
        dm_workspace
    )

    # =====================================================
    # DATASOURCE
    # =====================================================

    result["datasource"] = extract_datasource(
        dm_root
    )

    # =====================================================
    # SQL
    # =====================================================

    result["sql_queries"] = extract_sql_queries(
        dm_root
    )

    # =====================================================
    # DATASETS
    # =====================================================

    result["datasets"] = extract_datasets(
        dm_root
    )

    # =====================================================
    # PARAMETERS
    # =====================================================

    result["parameters"] = extract_dm_parameters(
        dm_root
    )

    return result