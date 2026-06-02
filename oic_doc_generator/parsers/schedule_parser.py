# =========================================================
# FILE:
# oic_doc_generator/parsers/schedule_parser.py
# =========================================================

import os

import xml.etree.ElementTree as ET

from oic_doc_generator.utils.xml_utils import (
    clean_tag
)


# =========================================================
# IS SCHEDULED INTEGRATION
# =========================================================

def is_scheduled_integration(
    extracted_iar
):

    for root, dirs, files in os.walk(
        extracted_iar
    ):

        if "schedule" in root.lower():

            for file in files:

                if file.lower().endswith(
                    ".xml"
                ):

                    return True

    return False


# =========================================================
# GET SCHEDULE INFORMATION
# =========================================================

def get_schedule_information(
    extracted_iar
):

    result = {

        "frequency":
            "No definida",

        "ical_expression":
            "",

        "schedule_name":
            ""
    }

    # =====================================================
    # SEARCH SCHEDULE XML
    # =====================================================

    for root, dirs, files in os.walk(
        extracted_iar
    ):

        if "schedule" not in root.lower():

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

                # =========================================
                # ITERATE XML
                # =========================================

                for elem in xml_root.iter():

                    tag = clean_tag(
                        elem.tag
                    )

                    text = (
                        elem.text.strip()
                        if elem.text
                        else ""
                    )

                    # =====================================
                    # ICAL EXPRESSION
                    # =====================================

                    if (
                        tag.lower()
                        ==
                        "ical-expression"
                    ):

                        result[
                            "ical_expression"
                        ] = text

                        result[
                            "frequency"
                        ] = convert_ical_to_text(
                            text
                        )

                    # =====================================
                    # NAME
                    # =====================================

                    elif (
                        tag.lower()
                        ==
                        "name"
                    ):

                        if not result[
                            "schedule_name"
                        ]:

                            result[
                                "schedule_name"
                            ] = text

            except:

                pass

    return result


# =========================================================
# CONVERT ICAL TO TEXT
# =========================================================

def convert_ical_to_text(
    ical_expression
):

    if not ical_expression:

        return "No definida"

    expression = (
        ical_expression.upper()
    )

    # =====================================================
    # MINUTELY
    # =====================================================

    if "FREQ=MINUTELY" in expression:

        interval = extract_interval(
            expression
        )

        return (
            f"Cada {interval} minuto(s)"
        )

    # =====================================================
    # HOURLY
    # =====================================================

    elif "FREQ=HOURLY" in expression:

        interval = extract_interval(
            expression
        )

        return (
            f"Cada {interval} hora(s)"
        )

    # =====================================================
    # DAILY
    # =====================================================

    elif "FREQ=DAILY" in expression:

        interval = extract_interval(
            expression
        )

        return (
            f"Cada {interval} día(s)"
        )

    # =====================================================
    # WEEKLY
    # =====================================================

    elif "FREQ=WEEKLY" in expression:

        interval = extract_interval(
            expression
        )

        return (
            f"Cada {interval} semana(s)"
        )

    # =====================================================
    # MONTHLY
    # =====================================================

    elif "FREQ=MONTHLY" in expression:

        interval = extract_interval(
            expression
        )

        return (
            f"Cada {interval} mes(es)"
        )

    return ical_expression


# =========================================================
# EXTRACT INTERVAL
# =========================================================

def extract_interval(
    expression
):

    try:

        parts = expression.split(
            ";"
        )

        for part in parts:

            if "INTERVAL=" in part:

                return (
                    part.split("=")[1]
                )

    except:

        pass

    return "1"