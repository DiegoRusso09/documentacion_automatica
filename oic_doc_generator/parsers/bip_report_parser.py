# =========================================================
# FILE:
# oic_doc_generator/parsers/bip_report_parser.py
# =========================================================

import os
import xml.etree.ElementTree as ET
from urllib.parse import unquote

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
# DECODE BIP PATH
# =========================================================

def decode_bip_path(
    encoded_path
):

    if not encoded_path:

        return ""

    decoded = unquote(
        encoded_path
    )

    decoded = decoded.replace(
        "+",
        " "
    )

    return decoded


# =========================================================
# EXTRACT REPORT PATH
# =========================================================

def extract_report_path(
    metadata_root
):

    if metadata_root is None:

        return ""

    for elem in metadata_root.iter():

        try:

            tag = clean_tag(
                elem.tag
            )

        except:

            continue

        if tag.lower() != "entry":

            continue

        key = ""
        value = ""

        for child in elem:

            try:

                child_tag = clean_tag(
                    child.tag
                )

            except:

                continue

            if child_tag.lower() == "key":

                if child.text:

                    key = child.text.strip()

            elif child_tag.lower() == "value":

                if child.text:

                    value = child.text.strip()

        if key == "path":

            return decode_bip_path(
                value
            )

    return ""


# =========================================================
# EXTRACT REPORT DISPLAY NAME
# =========================================================

def extract_report_display_name(
    metadata_root
):

    if metadata_root is None:

        return ""

    for elem in metadata_root.iter():

        try:

            tag = clean_tag(
                elem.tag
            )

        except:

            continue

        if tag.lower() != "entry":

            continue

        key = ""
        value = ""

        for child in elem:

            try:

                child_tag = clean_tag(
                    child.tag
                )

            except:

                continue

            if child_tag.lower() == "key":

                if child.text:

                    key = child.text.strip()

            elif child_tag.lower() == "value":

                if child.text:

                    value = child.text.strip()

        if key == "bip:DisplayName":

            return value

    return ""


# =========================================================
# EXTRACT DATA MODEL NAME
# =========================================================

def extract_data_model_name(
    report_root
):

    if report_root is None:

        return ""

    for elem in report_root.iter():

        try:

            tag = clean_tag(
                elem.tag
            )

        except:

            continue

        if tag.lower() != "datamodel":

            continue

        url = elem.attrib.get(
            "url",
            ""
        )

        if not url:

            continue

        file_name = os.path.basename(
            url
        )

        return (

            file_name

            .replace(
                ".xdm",
                ""
            )

            .strip()
        )

    return ""


# =========================================================
# EXTRACT TEMPLATES
# =========================================================

def extract_templates(
    report_root
):

    result = []

    if report_root is None:

        return result

    for elem in report_root.iter():

        try:

            tag = clean_tag(
                elem.tag
            )

        except:

            continue

        if tag.lower() != "template":

            continue

        template = {

            "label":
                elem.attrib.get(
                    "label",
                    ""
                ),

            "url":
                elem.attrib.get(
                    "url",
                    ""
                ),

            "type":
                elem.attrib.get(
                    "type",
                    ""
                ),

            "outputFormat":
                elem.attrib.get(
                    "outputFormat",
                    ""
                ),

            "defaultFormat":
                elem.attrib.get(
                    "defaultFormat",
                    ""
                )
        }

        result.append(
            template
        )

    return result


# =========================================================
# EXTRACT OUTPUT FORMATS
# =========================================================

def extract_output_formats(
    templates
):

    result = []

    for template in templates:

        output_format = template.get(
            "outputFormat",
            ""
        )

        if not output_format:

            continue

        if output_format not in result:

            result.append(
                output_format
            )

    return result


# =========================================================
# EXTRACT TEMPLATE FILES
# =========================================================

def extract_template_files(
    templates
):

    result = []

    for template in templates:

        url = template.get(
            "url",
            ""
        )

        if not url:

            continue

        if url not in result:

            result.append(
                url
            )

    return result


# =========================================================
# EXTRACT PARAMETERS
# =========================================================

def extract_report_parameters(
    report_root
):

    result = []

    if report_root is None:

        return result

    for elem in report_root.iter():

        try:

            tag = clean_tag(
                elem.tag
            )

        except:

            continue

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

        label = ""

        for child in elem:

            try:

                child_tag = clean_tag(
                    child.tag
                )

            except:

                continue

            if child_tag.lower() == "input":

                label = child.attrib.get(
                    "label",
                    ""
                )

        if not label:

            label = parameter_name

        result.append({

            "name":
                label,

            "code":
                parameter_name,

            "mandatory":
                "Si"
                if mandatory.lower() == "true"
                else "No",

            "description":
                ""
        })

    return result


# =========================================================
# PARSE BIP REPORT
# =========================================================

def parse_bip_report(
    report_workspace
):

    result = {

        "report_name": "",

        "report_path": "",

        "data_model": "",

        "templates": [],

        "output_formats": [],

        "template_files": [],

        "parameters": [],

        "report_xml_path": "",

        "metadata_xml_path": ""
    }

    if not report_workspace:

        return result

    # =====================================================
    # FIND FILES
    # =====================================================

    report_xml = find_file_recursive(

        report_workspace,

        "_report.xdo"
    )

    metadata_xml = find_file_recursive(

        report_workspace,

        "~metadata.meta"
    )

    result["report_xml_path"] = report_xml
    result["metadata_xml_path"] = metadata_xml

    # =====================================================
    # PARSE XML
    # =====================================================

    report_root = safe_xml_parse(
        report_xml
    )

    metadata_root = safe_xml_parse(
        metadata_xml
    )

    # =====================================================
    # REPORT NAME
    # =====================================================

    report_name = extract_report_display_name(
        metadata_root
    )

    if not report_name:

        if report_xml:

            report_name = os.path.basename(
                report_workspace
            )

    result["report_name"] = report_name

    # =====================================================
    # REPORT PATH
    # =====================================================

    result["report_path"] = extract_report_path(
        metadata_root
    )

    # =====================================================
    # DATA MODEL
    # =====================================================

    result["data_model"] = extract_data_model_name(
        report_root
    )

    # =====================================================
    # TEMPLATES
    # =====================================================

    templates = extract_templates(
        report_root
    )

    result["templates"] = templates

    # =====================================================
    # OUTPUT FORMATS
    # =====================================================

    result["output_formats"] = extract_output_formats(
        templates
    )

    # =====================================================
    # TEMPLATE FILES
    # =====================================================

    result["template_files"] = extract_template_files(
        templates
    )

    # =====================================================
    # PARAMETERS
    # =====================================================

    result["parameters"] = extract_report_parameters(
        report_root
    )

    return result