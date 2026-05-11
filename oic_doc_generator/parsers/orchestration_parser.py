# =========================================================
# FILE:
# oic_doc_generator/parsers/orchestration_parser.py
# =========================================================

import xml.etree.ElementTree as ET

from utils.xml_utils import (
    clean_tag,
    extract_application_from_refuri
)

from parsers.schedule_parser import (
    is_scheduled_integration
)

from parsers.project_parser import (
    build_application_map
)


# =========================================================
# GET ENDPOINT FLOWS
# =========================================================

def get_endpoint_flows(
    root,
    app_map
):

    endpoint_flows = {}

    # =====================================================
    # ROOT VALIDATION
    # =====================================================

    if root is None:

        return endpoint_flows

    # =====================================================
    # ITERATE ORCHESTRATIONS
    # =====================================================

    for orchestration in root.iter():

        try:

            tag = clean_tag(
                orchestration.tag
            ).lower()

        except:

            continue

        # =================================================
        # ORCHESTRATION
        # =================================================

        if tag != "orchestration":

            continue

        found_pick = False

        # =================================================
        # PICK
        # =================================================

        for pick in orchestration:

            try:

                pick_tag = clean_tag(
                    pick.tag
                ).lower()

            except:

                continue

            if pick_tag != "pick":

                continue

            found_pick = True

            # =============================================
            # PICK RECEIVE
            # =============================================

            for pick_receive in pick:

                try:

                    receive_tag = clean_tag(
                        pick_receive.tag
                    ).lower()

                except:

                    continue

                if receive_tag != "pickreceive":

                    continue

                refuri = (
                    pick_receive.attrib.get(
                        "refUri",
                        ""
                    )
                )

                app_ref = (
                    extract_application_from_refuri(
                        refuri
                    )
                )

                endpoint_name = app_ref

                # =========================================
                # REAL NAME FROM MAP
                # =========================================

                if app_ref in app_map:

                    endpoint_name = (
                        app_map[
                            app_ref
                        ].get(
                            "Invoke",
                            app_ref
                        )
                    )

                endpoint_flows[
                    endpoint_name
                ] = pick_receive

        # =================================================
        # FALLBACK:
        # SOME FLOWS DO NOT USE PICK/PICKRECEIVE
        # =================================================

        if not found_pick:

            first_invoke = None

            for child in orchestration.iter():

                try:

                    child_tag = clean_tag(
                        child.tag
                    ).lower()

                except:

                    continue

                if child_tag != "invoke":

                    continue

                first_invoke = child

                break

            if first_invoke is not None:

                endpoint_flows[
                    "Default_Endpoint"
                ] = orchestration

    # =====================================================
    # SCHEDULED FALLBACK
    # =====================================================

    if len(endpoint_flows) == 0:

        if is_possible_scheduled_flow(
            root
        ):

            endpoint_flows[
                "Scheduled_Integration"
            ] = root

    return endpoint_flows


# =========================================================
# IS POSSIBLE SCHEDULED FLOW
# =========================================================

def is_possible_scheduled_flow(
    root
):

    if root is None:

        return False

    try:

        xml_text = ET.tostring(
            root,
            encoding="unicode"
        )

    except:

        xml_text = str(root)

    keywords = [

        "schedule",

        "ics:schedule",

        "runEvery",

        "frequency",

        "recurrence",

        "scheduleReceive"
    ]

    for keyword in keywords:

        if keyword.lower() in xml_text.lower():

            return True

    return False


# =========================================================
# GENERATE DESCRIPTION
# =========================================================

def generate_description(
    endpoint_name,
    flow_node,
    applications,
    extracted_iar,
    project_root
):

    if flow_node is None:

        return (
            "No fue posible analizar "
            "el flujo."
        )

    app_map = build_application_map(
        applications
    )

    # =====================================================
    # ROOT
    # =====================================================

    root = project_root

    # =====================================================
    # BUILD PROCESSOR MAP
    # =====================================================

    processor_map = {}

    for elem in root.iter():

        try:

            tag = clean_tag(
                elem.tag
            ).lower()

        except:

            continue

        if tag != "processor":

            continue

        processor_name = elem.attrib.get(
            "name",
            ""
        )

        if processor_name:

            processor_map[
                processor_name
            ] = elem

    # =====================================================
    # GET PROCESSOR PROPERTY
    # =====================================================

    def get_processor_property(
        processor_node,
        property_name
    ):

        for child in processor_node.iter():

            try:

                tag = clean_tag(
                    child.tag
                ).lower()

            except:

                continue

            if tag != "property":

                continue

            if (
                child.attrib.get(
                    "name",
                    ""
                )
                ==
                property_name
            ):

                return child.attrib.get(
                    "value",
                    ""
                )

        return ""

    # =====================================================
    # DESCRIPTION
    # =====================================================

    steps = []

    first_connection = True

    # =====================================================
    # RECURSIVE FLOW
    # =====================================================

    def process_node(node):

        nonlocal first_connection

        for child in list(node):

            try:

                tag = clean_tag(
                    child.tag
                ).lower()

            except:

                continue

            # =================================================
            # INVOKE
            # =================================================

            if tag == "invoke":

                refuri = child.attrib.get(
                    "refUri",
                    ""
                )

                app_ref = (
                    extract_application_from_refuri(
                        refuri
                    )
                )

                if not app_ref:

                    continue

                invoke_name = app_ref

                connection_type = "UNKNOWN"

                if app_ref in app_map:

                    invoke_name = (
                        app_map[
                            app_ref
                        ].get(
                            "Invoke",
                            app_ref
                        )
                    )

                    connection_type = (
                        app_map[
                            app_ref
                        ].get(
                            "Tipo",
                            "UNKNOWN"
                        )
                    )

                if first_connection:

                    steps.append(

                        f"una conexión "
                        f"{connection_type} "
                        f"llamada "
                        f"{invoke_name}"
                    )

                    first_connection = False

                else:

                    steps.append(

                        f"se llama a una "
                        f"conexión "
                        f"{connection_type} "
                        f"llamada "
                        f"{invoke_name}"
                    )

            # =================================================
            # ASSIGNMENT
            # =================================================

            elif tag in [

                "assign",

                "assignment"
            ]:

                steps.append(
                    "se realiza un Assignment"
                )

            # =================================================
            # SWITCH
            # =================================================

            elif tag in [

                "switch",

                "router"
            ]:

                steps.append(
                    "se realiza un Switch"
                )

            # =================================================
            # WHILE
            # =================================================

            elif tag == "while":

                steps.append(
                    "se realiza un While"
                )

            # =================================================
            # STAGE FILE
            # =================================================

            elif tag == "stagefile":

                refuri = child.attrib.get(
                    "refUri",
                    ""
                )

                processor = processor_map.get(
                    refuri
                )

                operation = ""

                if processor is not None:

                    operation = (
                        get_processor_property(
                            processor,
                            "operation"
                        )
                    )

                if operation:

                    steps.append(

                        f"stageFile de operación "
                        f"{operation}"
                    )

                else:

                    steps.append(
                        "stageFile"
                    )

            # =================================================
            # FOR
            # =================================================

            elif tag == "for":

                refuri = child.attrib.get(
                    "refUri",
                    ""
                )

                processor = processor_map.get(
                    refuri
                )

                iteration_name = ""

                parallel = "false"

                if processor is not None:

                    parallel = (
                        get_processor_property(
                            processor,
                            "parallel"
                        )
                    )

                    for proc_child in processor.iter():

                        try:

                            proc_tag = clean_tag(
                                proc_child.tag
                            ).lower()

                        except:

                            continue

                        if proc_tag == "subrole":

                            if proc_child.text:

                                iteration_name = (
                                    proc_child.text.strip()
                                )

                mode = (
                    "paralela"
                    if parallel.lower() == "true"
                    else "secuencial"
                )

                if iteration_name:

                    steps.append(

                        f"Ahora comienza un For "
                        f"que itera sobre "
                        f"{iteration_name} "
                        f"de manera {mode}"
                    )

                else:

                    steps.append(
                        "Ahora comienza un For"
                    )

            # =================================================
            # SCOPE
            # =================================================

            elif tag == "scope":

                steps.append(
                    "se realiza un Scope"
                )

            # =================================================
            # RECURSIVE
            # =================================================

            process_node(child)

    # =====================================================
    # PROCESS FLOW
    # =====================================================

    process_node(flow_node)

    # =====================================================
    # EMPTY FLOW
    # =====================================================

    if len(steps) == 0:

        steps.append(
            "inicio del flujo"
        )

    # =====================================================
    # PREFIX
    # =====================================================

    if is_scheduled_integration(
        extracted_iar
    ):

        description = (
            "La integración "
            "programada comienza con: "
        )

    else:

        description = (
            f"El endpoint "
            f"{endpoint_name} "
            f"comienza con: "
        )

    # =====================================================
    # FINAL DESCRIPTION
    # =====================================================

    description += ", ".join(steps)

    description += "."

    return description