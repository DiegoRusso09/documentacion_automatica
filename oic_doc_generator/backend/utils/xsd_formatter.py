# =========================================================
# FILE:
# oic_doc_generator/utils/xsd_formatter.py
# =========================================================


# =========================================================
# INDENT
# =========================================================

def indent(
    level
):

    return "    " * level


# =========================================================
# BUILD ELEMENT
# =========================================================

def build_element(
    element,
    level=0
):

    name = element.get(
        "name",
        "FIELD"
    )

    data_type = element.get(
        "type",
        "xs:string"
    )

    data_type = data_type.replace(
        "xsd:",
        "xs:"
    )

    return (

        f"{indent(level)}"
        f'<xs:element '
        f'name="{name}" '
        f'type="{data_type}"/>'
    )


# =========================================================
# BUILD GROUP
# =========================================================

def build_group(
    group,
    level=0
):

    result = []

    group_name = group.get(
        "group_name",
        "GROUP"
    )

    result.append(

        f"{indent(level)}"
        f'<xs:element name="{group_name}">'
    )

    result.append(
        f"{indent(level + 1)}<xs:complexType>"
    )

    result.append(
        f"{indent(level + 2)}<xs:sequence>"
    )

    elements = group.get(
        "elements",
        []
    )

    for element in elements:

        result.append(

            build_element(
                element,
                level + 3
            )
        )

    result.append(
        f"{indent(level + 2)}</xs:sequence>"
    )

    result.append(
        f"{indent(level + 1)}</xs:complexType>"
    )

    result.append(
        f"{indent(level)}</xs:element>"
    )

    return "\n".join(result)


# =========================================================
# BUILD XSD TEXT
# =========================================================

def build_xsd_text(
    xsd_structure
):

    if not xsd_structure:

        return ""

    root_name = xsd_structure.get(
        "root_name",
        "DATA_DS"
    )

    groups = xsd_structure.get(
        "groups",
        []
    )

    result = []

    # =====================================================
    # XML HEADER
    # =====================================================

    result.append(
        '<?xml version="1.0" encoding="UTF-8"?>'
    )

    result.append("")

    # =====================================================
    # SCHEMA START
    # =====================================================

    result.append(
        '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">'
    )

    result.append("")

    # =====================================================
    # ROOT ELEMENT
    # =====================================================

    result.append(
        f'{indent(1)}<xs:element name="{root_name}">'
    )

    result.append(
        f'{indent(2)}<xs:complexType>'
    )

    result.append(
        f'{indent(3)}<xs:sequence>'
    )

    # =====================================================
    # GROUPS
    # =====================================================

    for group in groups:

        result.append(

            build_group(
                group,
                level=4
            )
        )

    # =====================================================
    # CLOSE ROOT
    # =====================================================

    result.append(
        f'{indent(3)}</xs:sequence>'
    )

    result.append(
        f'{indent(2)}</xs:complexType>'
    )

    result.append(
        f'{indent(1)}</xs:element>'
    )

    result.append("")
    result.append("</xs:schema>")

    return "\n".join(result)