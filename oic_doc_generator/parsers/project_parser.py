# =========================================================
# FILE:
# oic_doc_generator/parsers/project_parser.py
# =========================================================

import os
import xml.etree.ElementTree as ET

from utils.xml_utils import (
    clean_tag
)


# =========================================================
# FIND PROJECT XML
# =========================================================

def find_project_file(
    extracted_iar
):

    # =====================================================
    # PRIORITY:
    # PROJECT-INF/project.xml
    # =====================================================

    for root, dirs, files in os.walk(
        extracted_iar
    ):

        for file in files:

            if file.lower() != "project.xml":

                continue

            full_path = os.path.join(
                root,
                file
            )

            if "project-inf" in full_path.lower():

                return full_path

    # =====================================================
    # FALLBACK
    # =====================================================

    priority_files = [

        "project.xml",

        "icsproject",

        "integration-project.xml",

        "integrationproject.xml"
    ]

    for root, dirs, files in os.walk(
        extracted_iar
    ):

        for file in files:

            if file.lower() in priority_files:

                return os.path.join(
                    root,
                    file
                )

    return None


# =========================================================
# FIND PROJECT ATTRIBUTES
# =========================================================

def find_project_attributes_file(
    extracted_iar
):

    for root, dirs, files in os.walk(
        extracted_iar
    ):

        for file in files:

            if (

                file.lower()
                ==
                "ics_project_attributes.properties"
            ):

                return os.path.join(
                    root,
                    file
                )

    return None


# =========================================================
# GET PROJECT ROOT
# =========================================================

def get_project_root(
    extracted_iar
):

    project_file = find_project_file(
        extracted_iar
    )

    if not project_file:

        return None

    try:

        tree = ET.parse(
            project_file
        )

        return tree.getroot()

    except:

        return None


# =========================================================
# READ PROJECT ATTRIBUTES
# =========================================================

def read_project_attributes(
    extracted_iar
):

    result = {

        "project_name":
            "",

        "project_version":
            "",

        "project_description":
            ""
    }

    attributes_file = find_project_attributes_file(
        extracted_iar
    )

    if not attributes_file:

        return result

    try:

        with open(

            attributes_file,

            "r",

            encoding="utf-8"
        ) as file:

            lines = file.readlines()

    except:

        return result

    for line in lines:

        line = line.strip()

        if "=" not in line:

            continue

        key, value = line.split(
            "=",
            1
        )

        key = key.strip()
        value = value.strip()

        if key == "project_name":

            result[
                "project_name"
            ] = value

        elif key == "project_version":

            result[
                "project_version"
            ] = value

        elif key == "project_description":

            result[
                "project_description"
            ] = value

    return result


# =========================================================
# GET PROJECT NAME
# =========================================================

def get_project_name(
    extracted_iar
):

    root = get_project_root(
        extracted_iar
    )

    # =====================================================
    # PROJECT XML
    # =====================================================

    if root is not None:

        for elem in root.iter():

            try:

                tag = clean_tag(
                    elem.tag
                )

            except:

                continue

            if tag.lower() != "projectname":

                continue

            if elem.text:

                value = elem.text.strip()

                if value:

                    return value

    # =====================================================
    # FALLBACK PROPERTIES
    # =====================================================

    attributes = read_project_attributes(
        extracted_iar
    )

    if attributes.get(
        "project_name"
    ):

        return attributes[
            "project_name"
        ]

    return "Unknown Project"


# =========================================================
# GET PROJECT VERSION
# =========================================================

def get_project_version(
    extracted_iar
):

    root = get_project_root(
        extracted_iar
    )

    if root is not None:

        for elem in root.iter():

            try:

                tag = clean_tag(
                    elem.tag
                )

            except:

                continue

            if tag.lower() != "projectversion":

                continue

            if elem.text:

                value = elem.text.strip()

                if value:

                    return value

    attributes = read_project_attributes(
        extracted_iar
    )

    if attributes.get(
        "project_version"
    ):

        return attributes[
            "project_version"
        ]

    return "Unknown"


# =========================================================
# GET PROJECT DESCRIPTION
# =========================================================

def get_project_description(
    extracted_iar
):

    root = get_project_root(
        extracted_iar
    )

    if root is not None:

        for elem in root.iter():

            try:

                tag = clean_tag(
                    elem.tag
                )

            except:

                continue

            if tag.lower() != "projectdescription":

                continue

            if elem.text:

                value = elem.text.strip()

                if value:

                    return value

    attributes = read_project_attributes(
        extracted_iar
    )

    if attributes.get(
        "project_description"
    ):

        return attributes[
            "project_description"
        ]

    return ""


# =========================================================
# GET PROJECT STATE
# =========================================================

def get_project_state(
    extracted_iar
):

    return "ACTIVATED"


# =========================================================
# GET PROJECT TYPE
# =========================================================

def get_project_type(
    extracted_iar
):

    xml_text = ""

    root = get_project_root(
        extracted_iar
    )

    if root is not None:

        try:

            xml_text = ET.tostring(
                root,
                encoding="unicode"
            )

        except:

            pass

    lower = xml_text.lower()

    if (

        "schedule" in lower

        or

        "runevery" in lower

        or

        "recurrence" in lower
    ):

        return "SCHEDULED"

    return "REST"


# =========================================================
# MAP CONNECTION TYPE
# =========================================================

def map_connection_type(
    code
):

    if not code:

        return "UNKNOWN"

    lower = code.lower()

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

    return "UNKNOWN"


# =========================================================
# READ APPINSTANCE MAP
# =========================================================

def read_appinstance_map(
    extracted_iar
):

    result = {}

    appinstances_folder = None

    # =====================================================
    # FIND FOLDER
    # =====================================================

    for root, dirs, files in os.walk(
        extracted_iar
    ):

        if "appinstances" in root.lower():

            appinstances_folder = root

            break

    if not appinstances_folder:

        return result

    # =====================================================
    # XML FILES
    # =====================================================

    for file in os.listdir(
        appinstances_folder
    ):

        if not file.lower().endswith(
            ".xml"
        ):

            continue

        xml_path = os.path.join(
            appinstances_folder,
            file
        )

        try:

            tree = ET.parse(
                xml_path
            )

            root = tree.getroot()

        except:

            continue

        display_name = ""
        app_type = ""

        for elem in root.iter():

            try:

                tag = clean_tag(
                    elem.tag
                )

            except:

                continue

            if (

                tag.lower()
                ==
                "displayname"
            ):

                if elem.text:

                    display_name = (
                        elem.text.strip()
                    )

            elif (

                tag.lower()
                ==
                "applicationtyperef"
            ):

                if elem.text:

                    app_type = (
                        elem.text.strip()
                    )

        connection_code = os.path.splitext(
            file
        )[0]

        result[
            connection_code
        ] = {

            "displayName":
                display_name,

            "type":
                map_connection_type(
                    app_type
                )
        }

    return result


# =========================================================
# READ PROJECT XML
# =========================================================

def read_project_xml(
    extracted_iar
):

    root = get_project_root(
        extracted_iar
    )

    if root is None:

        return []

    appinstance_map = read_appinstance_map(
        extracted_iar
    )

    applications = []

    # =====================================================
    # APPLICATIONS
    # =====================================================

    for elem in root.iter():

        try:

            tag = clean_tag(
                elem.tag
            )

        except:

            continue

        if tag.lower() != "application":

            continue

        application_id = elem.attrib.get(
            "name",
            ""
        )

        if not application_id:

            continue

        adapter_name = ""
        adapter_code = ""
        adapter_type = ""

        # =================================================
        # ADAPTER
        # =================================================

        for child in elem.iter():

            try:

                child_tag = clean_tag(
                    child.tag
                )

            except:

                continue

            # =============================================
            # TYPE
            # =============================================

            if child_tag.lower() == "type":

                if child.text:

                    adapter_type = (
                        child.text.strip()
                    )

            # =============================================
            # CODE
            # =============================================

            elif child_tag.lower() == "code":

                if child.text:

                    adapter_code = (
                        child.text.strip()
                    )

            # =============================================
            # NAME
            # =============================================

            elif child_tag.lower() == "name":

                if child.text:

                    value = child.text.strip()

                    if (

                        value

                        and

                        not value.startswith(
                            "application_"
                        )
                    ):

                        adapter_name = value

        # =================================================
        # CONNECTION INFO
        # =================================================

        connection_name = adapter_code
        connection_type = map_connection_type(
            adapter_type
        )

        if adapter_code in appinstance_map:

            info = appinstance_map[
                adapter_code
            ]

            if info.get(
                "displayName"
            ):

                connection_name = info[
                    "displayName"
                ]

            if info.get(
                "type"
            ):

                connection_type = info[
                    "type"
                ]

        # =================================================
        # APPEND
        # =================================================

        applications.append({

            "Codigo":
                application_id,

            "Invoke":
                adapter_name,

            "Tipo":
                connection_type,

            "ConnectionName":
                connection_name,

            "Code":
                adapter_code
        })

    return applications


# =========================================================
# BUILD APPLICATION MAP
# =========================================================

def build_application_map(
    applications
):

    result = {}

    for app in applications:

        code = app.get(
            "Codigo"
        )

        if not code:

            continue

        result[
            code
        ] = app

    return result