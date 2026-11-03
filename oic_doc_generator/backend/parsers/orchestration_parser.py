# =========================================================
# FILE:
# oic_doc_generator/parsers/orchestration_parser.py
# =========================================================

import os
import re
import xml.etree.ElementTree as ET

from oic_doc_generator.backend.utils.xml_utils import (
    clean_tag,
    extract_application_from_refuri
)

from oic_doc_generator.backend.parsers.schedule_parser import (
    is_scheduled_integration
)

from oic_doc_generator.backend.parsers.project_parser import (
    build_application_map,
    find_project_file
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
#
# Construye un esquema jerárquico del flujo a partir de la
# orquestación real del .iar:
#
# - respeta qué actividades están dentro de cada While, For,
#   Switch (ramas con su condición) y Scope;
# - separa el manejo de errores del flujo principal;
# - agrupa actividades consecutivas del mismo tipo.
#
# El esquema es el texto que recibe la IA y, si la IA no está
# disponible, el que se escribe en el Word.
# =========================================================

# Etiquetas que no aportan a la descripción del flujo.
IGNORED_TAGS = {
    "integrationmetadata",
    "transformer",
    "receive",
    "schedulereceive",
    "pickreceive",
    "subscribe",
    "note"
}

# Actividades simples que se agrupan cuando son consecutivas.
GROUPABLE_KINDS = {
    "assignment": "Assignment",
    "stitch": "Stitch (actualización de variables)",
    "logger": "Logger (registro en el log de actividad)"
}

# Nombres por defecto que OIC pone a los grupos de Assignment.
DEFAULT_LABEL_PREFIXES = (
    "assign",
    "label"
)

# Condiciones más largas se omiten: en el documento no aportan
# y la IA no puede resumirlas sin riesgo de alterarlas.
MAX_EXPRESSION_LENGTH = 120

# Nombres por defecto que OIC pone a While/For/Switch/Scope.
DEFAULT_ACTION_NAME = re.compile(
    r"^(while|for|switch|scope|router)\d*$",
    re.IGNORECASE
)


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

    lines = render_flow_tree(
        analyze_flow(
            flow_node,
            applications,
            extracted_iar,
            project_root
        )
    )

    if not lines:
        lines = ["- Flujo sin actividades"]

    # =====================================================
    # HEADER
    # =====================================================

    if is_scheduled_integration(extracted_iar):

        header = "Integración programada. Flujo:"

    else:

        header = f"Endpoint {endpoint_name}. Flujo:"

    return "\n".join([header] + lines)


# =========================================================
# RENDER
# =========================================================

def render_flow_tree(items, depth=0):

    lines = []

    indent = "  " * depth

    for current in items:

        if current["kind"] in GROUPABLE_KINDS:

            text = (
                f"{current['count']} "
                f"{GROUPABLE_KINDS[current['kind']]}"
            )

            if current["names"]:
                text += f" ({', '.join(current['names'])})"

        else:

            text = current["text"]

        if current["children"]:
            text += ":"

        lines.append(f"{indent}- {text}")

        lines.extend(
            render_flow_tree(current["children"], depth + 1)
        )

    return lines


# =========================================================
# ANALYZE FLOW
# =========================================================
#
# Devuelve el árbol del flujo. Cada item:
#   {"kind", "text", "children", "count", "names"}
# y las llamadas (kind "invoke") llevan además "app" con los
# datos de la conexión o integración invocada. Lo usan la
# descripción y los diagramas.
# =========================================================

def analyze_flow(
    flow_node,
    applications,
    extracted_iar,
    project_root
):

    app_map = build_application_map(
        applications
    )

    root = project_root

    # =====================================================
    # PROJECT DIR (para leer expr.properties)
    # =====================================================

    project_file = find_project_file(
        extracted_iar
    )

    project_inf_dir = (
        os.path.dirname(project_file)
        if project_file
        else ""
    )

    # =====================================================
    # PROCESSOR MAP
    # =====================================================

    processor_map = {}

    for elem in root.iter():

        try:
            tag = clean_tag(elem.tag).lower()
        except Exception:
            continue

        if tag != "processor":
            continue

        processor_name = elem.attrib.get("name", "")

        if processor_name:
            processor_map[processor_name] = elem

    # =====================================================
    # HELPERS
    # =====================================================

    def child_text(node, child_tag):

        for child in node:

            try:
                if clean_tag(child.tag).lower() == child_tag:
                    return (child.text or "").strip()
            except Exception:
                continue

        return ""

    def get_processor(refuri):

        return processor_map.get(
            (refuri or "").split("/")[0]
        )

    def get_processor_property(processor_node, property_name):

        for child in processor_node.iter():

            try:
                tag = clean_tag(child.tag).lower()
            except Exception:
                continue

            if (
                tag == "property"
                and child.attrib.get("name", "") == property_name
            ):
                return child.attrib.get("value", "")

        return ""

    def read_expression(container):

        # Lee el primer expr.properties del nodo (processor u
        # output) y devuelve (nombre, texto legible).

        if container is None or not project_inf_dir:
            return "", ""

        for child in container.iter():

            try:
                tag = clean_tag(child.tag).lower()
            except Exception:
                continue

            location = child.attrib.get("location", "")

            if tag != "resource" or not location.endswith("expr.properties"):
                continue

            path = os.path.normpath(
                os.path.join(project_inf_dir, location)
            )

            if not os.path.isfile(path):
                continue

            values = {}

            with open(path, encoding="utf-8", errors="replace") as file:

                for line in file:

                    if " : " in line:
                        key, value = line.split(" : ", 1)
                        values[key.strip()] = value.strip()

            text = values.get("TextExpression", "")

            if len(text) > MAX_EXPRESSION_LENGTH:
                text = "una condición compleja"

            return values.get("ExpressionName", ""), text

        return "", ""

    def get_route_output(route_refuri):

        # route refUri: processor_X/output_Y
        parts = (route_refuri or "").split("/")

        processor = get_processor(route_refuri)

        if processor is None or len(parts) < 2:
            return None

        for child in processor:

            try:
                if (
                    clean_tag(child.tag).lower() == "output"
                    and child.attrib.get("name") == parts[1]
                ):
                    return child
            except Exception:
                continue

        return None

    # =====================================================
    # INVOKE
    # =====================================================

    def describe_invoke(node):

        app_ref = extract_application_from_refuri(
            node.attrib.get("refUri", "")
        )

        if not app_ref:
            return None

        info = app_map.get(app_ref, {})

        invoke_name = info.get("Invoke", app_ref)

        if info.get("IsIntegration", False):

            return (
                f"Llamada a la integración "
                f"{info.get('IntegrationCode', '')} "
                f"versión {info.get('IntegrationVersion', '')}, "
                f"endpoint {info.get('IntegrationService', '')} "
                f"({info.get('IntegrationOperation', '')}), "
                f"mediante el conector {invoke_name}"
            )

        return (
            f"Conexión {info.get('Tipo', 'UNKNOWN')} "
            f"{invoke_name}"
        )

    # =====================================================
    # BUILD TREE
    # =====================================================
    #
    # Cada item: {"kind", "text", "children", "count", "names"}
    # =====================================================

    def item(kind, text="", children=None):

        return {
            "kind": kind,
            "text": text,
            "children": children or [],
            "count": 1,
            "names": []
        }

    def build(node):

        items = []

        for child in list(node):

            try:
                tag = clean_tag(child.tag).lower()
            except Exception:
                continue

            if tag in IGNORED_TAGS:
                continue

            processor = get_processor(
                child.attrib.get("refUri", "")
            )

            processor_name = (
                child_text(processor, "processorname")
                if processor is not None
                else ""
            )

            # ---------------------------------------------
            # INVOKE
            # ---------------------------------------------

            if tag == "invoke":

                text = describe_invoke(child)

                if text:

                    invoke_item = item("invoke", text)

                    invoke_item["app"] = app_map.get(
                        extract_application_from_refuri(
                            child.attrib.get("refUri", "")
                        ),
                        {}
                    )

                    items.append(invoke_item)

            # ---------------------------------------------
            # ASSIGNMENTS (label = grupo de Assignment)
            # ---------------------------------------------

            elif tag == "label":

                label_items = build(child)

                label_name = child.attrib.get("name", "")

                if (
                    label_name
                    and not label_name.lower().startswith(
                        DEFAULT_LABEL_PREFIXES
                    )
                ):
                    for label_item in label_items:
                        if label_item["kind"] == "assignment":
                            label_item["names"].append(label_name)
                            break

                items.extend(label_items)

            elif tag in ["assign", "assignment"]:

                items.append(item("assignment"))

            elif tag == "stitch":

                items.append(item("stitch"))

            elif tag == "activitystreamlogger":

                items.append(item("logger"))

            # ---------------------------------------------
            # SWITCH
            # ---------------------------------------------

            elif tag in ["switch", "router"]:

                branches = []

                for route in child:

                    try:
                        if clean_tag(route.tag).lower() != "route":
                            continue
                    except Exception:
                        continue

                    name, expression = read_expression(
                        get_route_output(
                            route.attrib.get("refUri", "")
                        )
                    )

                    if name.lower() == "otherwise" or expression == "Else":

                        branch_text = "En cualquier otro caso (Otherwise)"

                    else:

                        branch_text = "Rama"

                        if name:
                            branch_text += f" {name}"

                        if expression:
                            branch_text += f", si se cumple: {expression}"

                    branches.append(
                        item(
                            "branch",
                            branch_text,
                            build(route) or [item("text", "Sin acciones")]
                        )
                    )

                items.append(
                    item(
                        "block",
                        "Switch que evalúa condiciones y continúa por una rama",
                        branches
                    )
                )

            # ---------------------------------------------
            # WHILE
            # ---------------------------------------------

            elif tag == "while":

                _, expression = read_expression(processor)

                text = "While"

                if (
                    processor_name
                    and not DEFAULT_ACTION_NAME.match(processor_name)
                ):
                    text += f" {processor_name}"

                text += (
                    f" que se repite mientras se cumpla: {expression}"
                    if expression
                    else " que se repite mientras se cumpla una condición"
                )

                items.append(item("block", text, build(child)))

            # ---------------------------------------------
            # FOR
            # ---------------------------------------------

            elif tag == "for":

                iteration_name = ""

                parallel = "false"

                if processor is not None:

                    parallel = get_processor_property(
                        processor,
                        "parallel"
                    )

                    for proc_child in processor.iter():

                        try:
                            proc_tag = clean_tag(proc_child.tag).lower()
                        except Exception:
                            continue

                        if proc_tag == "subrole" and proc_child.text:
                            iteration_name = proc_child.text.strip()

                mode = (
                    "paralela"
                    if (parallel or "").lower() == "true"
                    else "secuencial"
                )

                text = "For"

                if iteration_name:
                    text += f" que recorre cada elemento de {iteration_name}"

                text += f" de manera {mode}"

                items.append(item("block", text, build(child)))

            # ---------------------------------------------
            # SCOPE / MANEJO DE ERRORES
            # ---------------------------------------------

            elif tag in ["try", "scope"]:

                scope_name = child.attrib.get("name", "")

                if DEFAULT_ACTION_NAME.match(scope_name):
                    scope_name = ""

                items.append(
                    item(
                        "block",
                        f"Scope {scope_name}".strip(),
                        build(child)
                    )
                )

            elif tag == "globaltry":

                # Envuelve todo el flujo: sus actividades son el
                # flujo principal y su catchAll el manejo global.
                items.extend(build(child))

            elif tag in ["catchall", "catch"]:

                is_global = clean_tag(node.tag).lower() == "globaltry"

                items.append(
                    item(
                        "block",
                        (
                            "Manejo global de errores, si cualquier "
                            "paso del flujo falla"
                            if is_global
                            else "Si ocurre un error en este Scope"
                        ),
                        build(child) or [item("text", "Sin acciones")]
                    )
                )

            # ---------------------------------------------
            # OTRAS ACTIVIDADES
            # ---------------------------------------------

            elif tag == "stagefile":

                operation = (
                    get_processor_property(processor, "operation")
                    if processor is not None
                    else ""
                )

                items.append(
                    item(
                        "simple",
                        f"stageFile de operación {operation}"
                        if operation
                        else "stageFile"
                    )
                )

            elif tag == "notification":

                items.append(item("simple", "Envío de notificación por correo"))

            elif tag == "wait":

                _, expression = read_expression(processor)

                items.append(
                    item(
                        "simple",
                        f"Wait (espera de {expression} segundos)"
                        if expression
                        else "Wait (espera)"
                    )
                )

            elif tag == "reply":

                items.append(item("simple", "Reply (devuelve la respuesta al invocador)"))

            elif tag == "stop":

                items.append(item("simple", "Stop (fin del flujo)"))

            elif tag == "ehstop":

                items.append(item("simple", "Fin del manejo de errores"))

            # ---------------------------------------------
            # DESCONOCIDO: se recorre para no perder llamadas
            # ---------------------------------------------

            else:

                items.extend(build(child))

        return merge_consecutive(items)

    def merge_consecutive(items):

        merged = []

        for current in items:

            previous = merged[-1] if merged else None

            if (
                previous
                and current["kind"] in GROUPABLE_KINDS
                and previous["kind"] == current["kind"]
            ):
                previous["count"] += current["count"]
                previous["names"].extend(current["names"])
                continue

            merged.append(current)

        return merged

    # =====================================================
    # FLOW ROOT
    # =====================================================
    #
    # Para integraciones programadas el flujo puede llegar
    # como la raíz del proyecto: se usa su orquestación.
    # =====================================================

    if clean_tag(flow_node.tag).lower() not in [
        "orchestration",
        "pickreceive"
    ]:

        for elem in flow_node.iter():

            try:
                if clean_tag(elem.tag).lower() == "orchestration":
                    flow_node = elem
                    break
            except Exception:
                continue

    return build(flow_node)
