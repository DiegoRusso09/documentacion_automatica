# =========================================================
# FILE: oic_doc_generator/parsers/connections_parser.py
# =========================================================

import os
import re

import xml.etree.ElementTree as ET

from utils.xml_utils import (
    clean_tag,
    camel_to_snake_upper
)


# =========================================================
# MAP CONNECTION TYPE
# =========================================================

def map_connection_type(
    value
):

    if not value:

        return "UNKNOWN"

    lower = value.lower()

    if "dbaas" in lower:

        return "DBaaS"

    if "database" in lower:

        return "DBaaS"

    if "rest" in lower:

        return "REST"

    if "soap" in lower:

        return "SOAP"

    if "ftp" in lower:

        return "FTP"

    if "sftp" in lower:

        return "SFTP"

    if "erp" in lower:

        return "ERP"

    if "ociobjectstorage" in lower:

        return "OCI_OBJECT_STORAGE"

    if "stage" in lower:

        return "STAGE"

    if "file" in lower:

        return "FILE"

    return value


# =========================================================
# FIND APPLICATION FOLDER
# =========================================================

def find_application_folder(
    base_path,
    application_name
):

    for root, dirs, files in os.walk(
        base_path
    ):

        for d in dirs:

            if (
                d.lower()
                ==
                application_name.lower()
            ):

                return os.path.join(
                    root,
                    d
                )

    return None


# =========================================================
# FIND JCA FILE
# =========================================================

def find_jca_file(
    application_folder
):

    if not application_folder:

        return None

    for root, dirs, files in os.walk(
        application_folder
    ):

        for file in files:

            if file.endswith(
                ".jca"
            ):

                return os.path.join(
                    root,
                    file
                )

    return None


# =========================================================
# ANALYZE DBAAS JCA
# =========================================================

def analyze_dbaas_jca(
    application_folder
):

    result = {

        "Operacion": "",

        "Tabla": "",

        "Package": "",

        "Procedure": "",

        "SQL": ""
    }

    jca_file = find_jca_file(
        application_folder
    )

    if not jca_file:

        return result

    with open(

        jca_file,

        "r",

        encoding="utf-8",

        errors="ignore"

    ) as f:

        content = f.read()

    # =====================================================
    # STORED PROCEDURE
    # =====================================================

    if (
        "DBStoredProcedureInteractionSpec"
        in content
    ):

        result["Operacion"] = (
            "Stored Procedure"
        )

        package_match = re.search(

            r'PackageName\" value=\"([^\"]+)\"',

            content
        )

        procedure_match = re.search(

            r'ProcedureName\" value=\"([^\"]+)\"',

            content
        )

        if package_match:

            result["Package"] = (
                package_match.group(1)
            )

        if procedure_match:

            result["Procedure"] = (
                procedure_match.group(1)
            )

    # =====================================================
    # PURE SQL
    # =====================================================

    if (
        "DBPureSQLInteractionSpec"
        in content
    ):

        result["Operacion"] = (
            "SQL Puro"
        )

        sql_match = re.search(

            r'SqlString\" value=\"([^\"]+)\"',

            content
        )

        if sql_match:

            result["SQL"] = (
                sql_match.group(1)
            )

            table_match = re.search(

                r'from\s+([a-zA-Z0-9_\.]+)',

                result["SQL"],

                re.IGNORECASE
            )

            if table_match:

                result["Tabla"] = (
                    table_match.group(1)
                )

    # =====================================================
    # SELECT
    # =====================================================

    if (
        "DBReadInteractionSpec"
        in content
    ):

        if "QueryName" in content:

            result["Operacion"] = (
                "Select"
            )

        descriptor_match = re.search(

            r'DescriptorName\" value=\"([^\"]+)\"',

            content
        )

        if descriptor_match:

            descriptor = (
                descriptor_match.group(1)
            )

            if "." in descriptor:

                descriptor = descriptor.split(
                    "."
                )[-1]

            result["Tabla"] = (
                camel_to_snake_upper(
                    descriptor
                )
            )

    # =====================================================
    # INSERT UPDATE DELETE
    # =====================================================

    if (
        "DBWriteInteractionSpec"
        in content
    ):

        dml_match = re.search(

            r'DmlType\" value=\"([^\"]+)\"',

            content
        )

        if dml_match:

            result["Operacion"] = (

                dml_match.group(1)
                .capitalize()
            )

        descriptor_match = re.search(

            r'DescriptorName\" value=\"([^\"]+)\"',

            content
        )

        if descriptor_match:

            descriptor = (
                descriptor_match.group(1)
            )

            if "." in descriptor:

                descriptor = descriptor.split(
                    "."
                )[-1]

            result["Tabla"] = (
                camel_to_snake_upper(
                    descriptor
                )
            )

    return result


# =========================================================
# GET CONNECTIONS INFORMATION
# =========================================================

def get_connections_information(
    extracted_iar
):

    result = []

    for root, dirs, files in os.walk(
        extracted_iar
    ):

        if "appinstances" not in root.lower():

            continue

        for file in files:

            if not file.lower().endswith(
                ".xml"
            ):

                continue

            xml_path = os.path.join(
                root,
                file
            )

            try:

                tree = ET.parse(
                    xml_path
                )

                xml_root = tree.getroot()

            except:

                continue

            conn_data = {

                "name": "",

                "type": "",

                "security_policy": "",

                "agent_group": "",

                "properties": {}
            }

            current_property = None

            # =================================================
            # ITER XML
            # =================================================

            for elem in xml_root.iter():

                try:

                    tag = clean_tag(
                        elem.tag
                    )

                except:

                    continue

                text = (
                    elem.text.strip()
                    if elem.text
                    else ""
                )

                # =============================================
                # DISPLAY NAME (PRIORITY)
                # =============================================

                if tag == "displayName":

                    conn_data[
                        "name"
                    ] = text

                # =============================================
                # FALLBACK NAME
                # =============================================

                elif (

                    tag == "name"

                    and

                    not conn_data["name"]
                ):

                    conn_data[
                        "name"
                    ] = text

                # =============================================
                # TYPE
                # =============================================

                elif (
                    tag
                    ==
                    "applicationTypeRef"
                ):

                    conn_data[
                        "type"
                    ] = map_connection_type(
                        text
                    )

                # =============================================
                # SECURITY POLICY
                # =============================================

                elif (
                    tag
                    ==
                    "securityPolicy"
                ):

                    conn_data[
                        "security_policy"
                    ] = text

                # =============================================
                # AGENT GROUP
                # =============================================

                elif (
                    tag
                    ==
                    "agentDefinition"
                ):

                    conn_data[
                        "agent_group"
                    ] = text

                # =============================================
                # PROPERTY NAME
                # =============================================

                elif (
                    tag
                    ==
                    "connectionProperty"
                ):

                    current_property = {}

                elif (
                    tag
                    ==
                    "name"
                ):

                    if current_property is not None:

                        current_property[
                            "name"
                        ] = text

                elif (
                    tag
                    ==
                    "value"
                ):

                    if current_property is not None:

                        current_property[
                            "value"
                        ] = text

                        property_name = (
                            current_property.get(
                                "name",
                                ""
                            )
                        )

                        property_value = (
                            current_property.get(
                                "value",
                                ""
                            )
                        )

                        if property_name:

                            conn_data[
                                "properties"
                            ][
                                property_name
                            ] = property_value

                        current_property = None

            # =================================================
            # FALLBACK NAME FROM FILE
            # =================================================

            if not conn_data["name"]:

                conn_data["name"] = (
                    os.path.splitext(
                        file
                    )[0]
                )

            result.append(
                conn_data
            )

    return result


# =========================================================
# GET CONNECTION XMLS
# =========================================================

def get_connection_xmls(
    extracted_iar
):

    return get_connections_information(
        extracted_iar
    )