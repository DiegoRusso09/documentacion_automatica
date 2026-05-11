# =========================================================
# core/xml_utils.py
# =========================================================

import re
import xml.etree.ElementTree as ET


# =========================================================
# CLEAN XML TAG
# =========================================================

def clean_tag(tag):

    if not tag:
        return ""

    if "}" in tag:

        return tag.split(
            "}",
            1
        )[1]

    return tag


# =========================================================
# PARSE XML FILE
# =========================================================

def parse_xml_file(xml_path):

    try:

        tree = ET.parse(xml_path)

        return tree

    except Exception:

        return None


# =========================================================
# GET XML ROOT
# =========================================================

def get_xml_root(xml_path):

    tree = parse_xml_file(
        xml_path
    )

    if not tree:
        return None

    return tree.getroot()


# =========================================================
# XML TO STRING
# =========================================================

def xml_to_string(element):

    try:

        return ET.tostring(
            element,
            encoding="unicode"
        )

    except Exception:

        return ""


# =========================================================
# FIND FIRST ELEMENT BY TAG
# =========================================================

def find_first_element(
    root,
    tag_name
):

    if root is None:
        return None

    for elem in root.iter():

        if clean_tag(elem.tag) == tag_name:

            return elem

    return None


# =========================================================
# FIND ALL ELEMENTS BY TAG
# =========================================================

def find_all_elements(
    root,
    tag_name
):

    results = []

    if root is None:
        return results

    for elem in root.iter():

        if clean_tag(elem.tag) == tag_name:

            results.append(elem)

    return results


# =========================================================
# GET ELEMENT TEXT
# =========================================================

def get_element_text(element):

    if element is None:
        return ""

    if element.text is None:
        return ""

    return element.text.strip()


# =========================================================
# GET CHILD TEXT
# =========================================================

def get_child_text(
    parent,
    child_tag
):

    if parent is None:
        return ""

    for child in parent:

        if clean_tag(child.tag) == child_tag:

            return get_element_text(
                child
            )

    return ""


# =========================================================
# GET ATTRIBUTE
# =========================================================

def get_attribute(
    element,
    attribute_name
):

    if element is None:
        return ""

    return element.attrib.get(
        attribute_name,
        ""
    )


# =========================================================
# SAFE FIND TEXT
# =========================================================

def safe_find_text(
    root,
    tag_name
):

    elem = find_first_element(
        root,
        tag_name
    )

    return get_element_text(
        elem
    )


# =========================================================
# EXTRACT APPLICATION FROM REFURI
# =========================================================

def extract_application_from_refuri(
    refuri
):

    if not refuri:
        return None

    match = re.search(
        r'(application_\d+)',
        refuri
    )

    if match:

        return match.group(1)

    return None


# =========================================================
# CAMEL TO SNAKE UPPER
# =========================================================

def camel_to_snake_upper(name):

    if not name:
        return ""

    s1 = re.sub(
        '(.)([A-Z][a-z]+)',
        r'\1_\2',
        name
    )

    s2 = re.sub(
        '([a-z0-9])([A-Z])',
        r'\1_\2',
        s1
    )

    return s2.upper()


# =========================================================
# SANITIZE TEXT
# =========================================================

def sanitize_text(text):

    if not text:
        return ""

    text = text.replace(
        "\n",
        " "
    )

    text = text.replace(
        "\r",
        " "
    )

    text = text.replace(
        "\t",
        " "
    )

    text = re.sub(
        r'\s+',
        ' ',
        text
    )

    return text.strip()


# =========================================================
# XML ELEMENT EXISTS
# =========================================================

def element_exists(
    root,
    tag_name
):

    elem = find_first_element(
        root,
        tag_name
    )

    return elem is not None


# =========================================================
# GET ALL TAG VALUES
# =========================================================

def get_all_tag_values(
    root,
    tag_name
):

    values = []

    elements = find_all_elements(
        root,
        tag_name
    )

    for elem in elements:

        text = get_element_text(
            elem
        )

        if text:

            values.append(text)

    return values


# =========================================================
# READ PROPERTIES FILE
# =========================================================

def read_properties_file(file_path):

    properties = {}

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            lines = f.readlines()

        for line in lines:

            line = line.strip()

            if not line:
                continue

            if line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split(
                "=",
                1
            )

            properties[
                key.strip()
            ] = value.strip()

    except Exception:

        pass

    return properties


# =========================================================
# PRETTY ICAL EXPRESSION
# =========================================================

def prettify_ical_expression(
    ical_expression
):

    if not ical_expression:

        return "No definido"

    expression = (
        ical_expression.upper()
    )

    freq_match = re.search(
        r'FREQ=([^;]+)',
        expression
    )

    interval_match = re.search(
        r'INTERVAL=([^;]+)',
        expression
    )

    freq = (
        freq_match.group(1)
        if freq_match
        else ""
    )

    interval = (
        interval_match.group(1)
        if interval_match
        else "1"
    )

    if freq == "MINUTELY":

        return (
            f"Cada {interval} minuto(s)"
        )

    if freq == "HOURLY":

        return (
            f"Cada {interval} hora(s)"
        )

    if freq == "DAILY":

        return (
            f"Cada {interval} día(s)"
        )

    if freq == "WEEKLY":

        return (
            f"Cada {interval} semana(s)"
        )

    if freq == "MONTHLY":

        return (
            f"Cada {interval} mes(es)"
        )

    return ical_expression