# =========================================================
# FILE:
# oic_doc_generator/parsers/service_parser.py
# =========================================================

import os

import xml.etree.ElementTree as ET

from oic_doc_generator.backend.utils.xml_utils import (
    clean_tag
)


# =========================================================
# GET REQUEST RESPONSE SCHEMAS
# =========================================================

def get_request_response_schemas(
    extracted_iar
):

    services = {}

    for root, dirs, files in os.walk(
        extracted_iar
    ):

        for file in files:

            file_lower = file.lower()

            if not (

                file_lower.endswith(".wsdl")

                or

                file_lower.endswith(".xsd")
            ):

                continue

            full_path = os.path.join(
                root,
                file
            )

            try:

                parsed = parse_service_file(
                    full_path
                )

                if not parsed:

                    continue

                endpoint = parsed[
                    "endpoint"
                ]

                # =========================================
                # CREATE SERVICE
                # =========================================

                if endpoint not in services:

                    services[endpoint] = {

                        "endpoint":
                            endpoint,

                        "request_elements":
                            [],

                        "response_elements":
                            [],

                        "request_is_array":
                            False,

                        "response_is_array":
                            False
                    }

                # =========================================
                # MERGE REQUEST
                # =========================================

                services[
                    endpoint
                ][
                    "request_elements"
                ].extend(
                    parsed[
                        "request_elements"
                    ]
                )

                # =========================================
                # MERGE RESPONSE
                # =========================================

                services[
                    endpoint
                ][
                    "response_elements"
                ].extend(
                    parsed[
                        "response_elements"
                    ]
                )

                # =========================================
                # KEEP ARRAY FLAG
                # =========================================

                if parsed.get(
                    "request_is_array",
                    False
                ):

                    services[
                        endpoint
                    ][
                        "request_is_array"
                    ] = True

                if parsed.get(
                    "response_is_array",
                    False
                ):

                    services[
                        endpoint
                    ][
                        "response_is_array"
                    ] = True

            except:

                pass

    # =====================================================
    # FINAL CLEAN
    # =====================================================

    final_services = []

    for service in services.values():

        service[
            "request_elements"
        ] = remove_duplicates(
            service[
                "request_elements"
            ]
        )

        service[
            "response_elements"
        ] = remove_duplicates(
            service[
                "response_elements"
            ]
        )

        # =================================================
        # IGNORE EMPTY
        # =================================================

        if (
            len(
                service[
                    "request_elements"
                ]
            ) == 0

            and

            len(
                service[
                    "response_elements"
                ]
            ) == 0
        ):

            continue

        final_services.append(
            service
        )

    return final_services


# =========================================================
# PARSE SERVICE FILE
# =========================================================

def parse_service_file(
    file_path
):

    tree = ET.parse(
        file_path
    )

    root = tree.getroot()

    endpoint = extract_endpoint_name(
        root,
        file_path
    )

    request_elements = []

    response_elements = []

    request_is_array = False

    response_is_array = False

    # =====================================================
    # SEARCH SCHEMAS
    # =====================================================

    for schema in root.iter():

        tag = clean_tag(
            schema.tag
        )

        if tag != "schema":

            continue

        # =================================================
        # REQUEST
        # =================================================

        request_data = extract_template_parameters(
            schema
        )

        if request_data:

            request_elements.extend(
                request_data["elements"]
            )

            if request_data["is_array"]:

                request_is_array = True

        # =================================================
        # RESPONSE
        # =================================================

        response_data = extract_response_wrapper(
            schema
        )

        if response_data:

            response_elements.extend(
                response_data["elements"]
            )

            if response_data["is_array"]:

                response_is_array = True

    # =====================================================
    # IGNORE EMPTY
    # =====================================================

    if (
        len(request_elements)
        ==
        0

        and

        len(response_elements)
        ==
        0
    ):

        return None

    return {

        "endpoint":
            endpoint,

        "request_elements":
            remove_duplicates(
                request_elements
            ),

        "response_elements":
            remove_duplicates(
                response_elements
            ),

        "request_is_array":
            request_is_array,

        "response_is_array":
            response_is_array
    }


# =========================================================
# EXTRACT ENDPOINT
# =========================================================

def extract_endpoint_name(
    root,
    file_path
):

    target_namespace = root.attrib.get(
        "targetNamespace",
        ""
    )

    if "/" in target_namespace:

        parts = target_namespace.split("/")

        for part in reversed(parts):

            if (
                part
                and
                "types"
                not in part.lower()
                and
                "rest"
                not in part.lower()
                and
                "request"
                not in part.lower()
            ):

                return part

    file_name = os.path.basename(
        file_path
    )

    return os.path.splitext(
        file_name
    )[0]


# =========================================================
# EXTRACT TEMPLATE PARAMETERS
# =========================================================

def extract_template_parameters(
    schema
):

    result = []

    is_array = False

    for complex_type in schema.iter():

        tag = clean_tag(
            complex_type.tag
        )

        if (
            tag
            !=
            "complexType"
        ):

            continue

        type_name = complex_type.attrib.get(
            "name",
            ""
        )

        if (
            type_name
            !=
            "TemplateParameters"
        ):

            continue

        for elem in complex_type.iter():

            child_tag = clean_tag(
                elem.tag
            )

            if child_tag != "element":

                continue

            name = elem.attrib.get(
                "name",
                ""
            )

            data_type = elem.attrib.get(
                "type",
                ""
            )

            if not name:

                continue

            # =============================================
            # ARRAY
            # =============================================

            if (
                name
                ==
                "topLevelArray"
            ):

                is_array = True

                continue

            # =============================================
            # IGNORE WRAPPERS
            # =============================================

            if name in [

                "response-wrapper",

                "request-wrapper"
            ]:

                continue

            result.append({

                "name":
                    name,

                "type":
                    normalize_type(
                        data_type
                    )
            })

    return {

        "elements":
            result,

        "is_array":
            is_array
    }


# =========================================================
# EXTRACT RESPONSE WRAPPER
# =========================================================

def extract_response_wrapper(
    schema
):

    result = []

    is_array = False

    for element in schema.iter():

        tag = clean_tag(
            element.tag
        )

        if tag != "element":

            continue

        element_name = element.attrib.get(
            "name",
            ""
        )

        if (
            element_name
            !=
            "response-wrapper"
        ):

            continue

        for child in element.iter():

            child_tag = clean_tag(
                child.tag
            )

            if child_tag != "element":

                continue

            name = child.attrib.get(
                "name",
                ""
            )

            data_type = child.attrib.get(
                "type",
                ""
            )

            if not name:

                continue

            # =============================================
            # ARRAY
            # =============================================

            if (
                name
                ==
                "topLevelArray"
            ):

                is_array = True

                continue

            # =============================================
            # IGNORE WRAPPERS
            # =============================================

            if name in [

                "response-wrapper",

                "request-wrapper"
            ]:

                continue

            result.append({

                "name":
                    name,

                "type":
                    normalize_type(
                        data_type
                    )
            })

    return {

        "elements":
            result,

        "is_array":
            is_array
    }


# =========================================================
# NORMALIZE TYPE
# =========================================================

def normalize_type(
    data_type
):

    if not data_type:

        return "string"

    data_type = data_type.lower()

    replacements = {

        "xsd:string":
            "string",

        "xs:string":
            "string",

        "xsd:date":
            "date",

        "xs:date":
            "date",

        "xsd:datetime":
            "datetime",

        "xs:datetime":
            "datetime",

        "xsd:decimal":
            "number",

        "xs:decimal":
            "number",

        "xsd:int":
            "number",

        "xs:int":
            "number"
    }

    return replacements.get(
        data_type,
        data_type
    )


# =========================================================
# REMOVE DUPLICATES
# =========================================================

def remove_duplicates(
    elements
):

    unique = []

    existing = set()

    for element in elements:

        key = (
            element["name"],
            element["type"]
        )

        if key in existing:

            continue

        existing.add(key)

        unique.append(
            element
        )

    return unique