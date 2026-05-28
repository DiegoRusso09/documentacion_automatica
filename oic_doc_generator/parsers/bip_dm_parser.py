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
# EXTRACT DATASET SQLS
# =========================================================

def extract_dataset_sqls(
    dm_root
):

    result = []

    if dm_root is None:

        return result

    # =====================================================
    # ITERATE DATASETS
    # =====================================================

    for elem in dm_root.iter():

        try:

            tag = clean_tag(
                elem.tag
            )

        except:

            continue

        if tag.lower() != "dataset":

            continue

        dataset_name = elem.attrib.get(
            "name",
            ""
        )

        sql_text = ""

        datasource = ""

        # =================================================
        # SEARCH SQL
        # =================================================

        for child in elem.iter():

            try:

                child_tag = clean_tag(
                    child.tag
                )

            except:

                continue

            if child_tag.lower() != "sql":

                continue

            datasource = child.attrib.get(
                "dataSourceRef",
                ""
            )

            if child.text:

                sql_text = child.text.strip()

            break

        result.append({

            "name":
                dataset_name,

            "datasource":
                datasource,

            "sql":
                sql_text
        })

    return result


# =========================================================
# EXTRACT OUTPUT STRUCTURE
# =========================================================

def extract_output_structure(
    dm_root
):

    result = {

        "root_name": "",

        "groups": []
    }

    if dm_root is None:

        return result

    # =====================================================
    # SEARCH OUTPUT
    # =====================================================

    for elem in dm_root.iter():

        try:

            tag = clean_tag(
                elem.tag
            )

        except:

            continue

        if tag.lower() != "output":

            continue

        result["root_name"] = elem.attrib.get(
            "rootName",
            "DATA_DS"
        )

        # =================================================
        # GROUPS
        # =================================================

        for group in elem.iter():

            try:

                group_tag = clean_tag(
                    group.tag
                )

            except:

                continue

            if group_tag.lower() != "group":

                continue

            group_name = group.attrib.get(
                "name",
                ""
            )

            group_source = group.attrib.get(
                "source",
                ""
            )

            elements = []

            # =============================================
            # ELEMENTS
            # =============================================

            for field in group.iter():

                try:

                    field_tag = clean_tag(
                        field.tag
                    )

                except:

                    continue

                if field_tag.lower() != "element":

                    continue

                elements.append({

                    "name":
                        field.attrib.get(
                            "name",
                            ""
                        ),

                    "type":
                        field.attrib.get(
                            "dataType",
                            "xsd:string"
                        )
                })

            result["groups"].append({

                "group_name":
                    group_name,

                "source":
                    group_source,

                "elements":
                    elements
            })

        break

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

        "dataset_sqls": [],

        "xsd_structure": {},

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
    # DATASET SQLS
    # =====================================================

    result["dataset_sqls"] = extract_dataset_sqls(
        dm_root
    )

    # =====================================================
    # XSD STRUCTURE
    # =====================================================

    result["xsd_structure"] = extract_output_structure(
        dm_root
    )

    # =====================================================
    # PARAMETERS
    # =====================================================

    result["parameters"] = extract_dm_parameters(
        dm_root
    )

    return result