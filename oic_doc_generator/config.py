# =========================================================
# FILE: config.py
# =========================================================

import re


# =========================================================
# CLEAN XML TAG
# =========================================================

def clean_tag(tag):

    if "}" in tag:

        return tag.split(
            "}",
            1
        )[1]

    return tag


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
# DETECT CONNECTION TYPE
# =========================================================

def detect_connection_type(
    adapter_code,
    adapter_type
):

    value = (
        f"{adapter_code} "
        f"{adapter_type}"
    ).lower()

    if (
        "dbaas" in value
        or
        "db" in value
    ):

        return "DBaaS"

    if "rest" in value:

        return "REST"

    if "soap" in value:

        return "SOAP"

    if "ftp" in value:

        return "FTP"

    if "sftp" in value:

        return "SFTP"

    if "erp" in value:

        return "ERP Cloud"

    return "Unknown"