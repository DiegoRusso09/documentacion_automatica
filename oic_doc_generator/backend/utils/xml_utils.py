# =========================================================
# FILE: utils/xml_utils.py
# =========================================================

import re


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
# GET TEXT
# =========================================================

def get_text(elem):

    if elem is None:
        return ""

    if elem.text is None:
        return ""

    return elem.text.strip()


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

    text = text.strip()

    return text


# =========================================================
# SAFE FIND
# =========================================================

def safe_find(
    parent,
    tag_name
):

    if parent is None:
        return None

    for child in parent:

        tag = clean_tag(
            child.tag
        )

        if tag == tag_name:

            return child

    return None


# =========================================================
# SAFE FIND ALL
# =========================================================

def safe_find_all(
    parent,
    tag_name
):

    results = []

    if parent is None:
        return results

    for child in parent:

        tag = clean_tag(
            child.tag
        )

        if tag == tag_name:

            results.append(
                child
            )

    return results