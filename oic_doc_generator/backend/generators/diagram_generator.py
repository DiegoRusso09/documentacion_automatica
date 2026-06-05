# =========================================================
# FILE: diagram_generator.py
# =========================================================

import os
import re
import tempfile

from graphviz import Digraph


# =========================================================
# SANITIZE TEXT
# =========================================================

def sanitize_text(text):

    if not text:
        return "UNKNOWN"

    text = str(text)

    text = re.sub(
        r'["\'<>]',
        '',
        text
    )

    return text.strip()


# =========================================================
# DETECT TARGET
# =========================================================

def detect_target(description):

    if not description:
        return "SYSTEM"

    match = re.search(
        r'De tipo ([^,\.]+)',
        description,
        re.IGNORECASE
    )

    if match:

        return sanitize_text(
            match.group(1)
        )

    return "SYSTEM"


# =========================================================
# GENERATE PNG
# =========================================================

def generate_sequence_diagram_png(
    endpoint_name,
    rows,
    integration_type="REST"
):

    temp_dir = tempfile.mkdtemp()

    png_file = os.path.join(
        temp_dir,
        "diagram.png"
    )

    graph = Digraph(
        name="SequenceDiagram",
        format="png"
    )

    graph.attr(
        rankdir="LR"
    )

    graph.attr(
        bgcolor="white"
    )

    graph.attr(
        fontsize="10"
    )

    graph.attr(
        fontname="Arial"
    )

    graph.attr(
        nodesep="0.7"
    )

    graph.attr(
        ranksep="1"
    )

    graph.attr(
        splines="ortho"
    )

    graph.attr(
        pad="0.3"
    )

    graph.attr(
        dpi="200"
    )

    # =====================================================
    # START NODE
    # =====================================================

    if integration_type.lower() == "scheduled":

        start_node = "SCHEDULER"

        graph.node(
            start_node,
            shape="box"
        )

        graph.node(
            endpoint_name,
            shape="box",
            style="filled",
            fillcolor="#D9EAD3"
        )

        graph.edge(
            start_node,
            endpoint_name,
            label="Trigger"
        )

    else:

        start_node = "CLIENT"

        graph.node(
            start_node,
            shape="box"
        )

        graph.node(
            endpoint_name,
            shape="box",
            style="filled",
            fillcolor="#D9EAD3"
        )

        graph.edge(
            start_node,
            endpoint_name,
            label="Request"
        )

    # =====================================================
    # FLOW
    # =====================================================

    previous = endpoint_name

    for row in rows[1:]:

        action = sanitize_text(

            row.get(
                "Nombre Acción",
                "ACTION"
            )
        )

        description = row.get(
            "Descripción de la Acción",
            ""
        )

        target = detect_target(
            description
        )

        node_id = (
            f"{target}_{action}"
        )

        graph.node(

            node_id,

            label=(
                f"{target}\n"
                f"{action}"
            ),

            shape="box"
        )

        graph.edge(
            previous,
            node_id
        )

        previous = node_id

    # =====================================================
    # END
    # =====================================================

    if integration_type.lower() != "scheduled":

        graph.edge(
            previous,
            "CLIENT",
            label="Response"
        )

    graph.render(
        filename="diagram",
        directory=temp_dir,
        cleanup=True
    )

    if not os.path.exists(
        png_file
    ):

        raise Exception(
            "Graphviz no generó PNG"
        )

    return png_file