# =========================================================
# FILE:
# oic_doc_generator/generators/erd_generator.py
# =========================================================

import os
import uuid
import tempfile

import networkx as nx
import matplotlib.pyplot as plt


# =========================================================
# GENERATE OUTPUT PATH
# =========================================================

def generate_output_path():

    return os.path.join(

        tempfile.gettempdir(),

        f"erd_{uuid.uuid4()}.png"
    )


# =========================================================
# BUILD GRAPH
# =========================================================

def build_graph(
    tables
):

    graph = nx.DiGraph()

    for table in tables:

        table_name = table.get(
            "table_name",
            ""
        )

        graph.add_node(
            table_name
        )

    for table in tables:

        source_table = table.get(
            "table_name",
            ""
        )

        for fk in table.get(
            "foreign_keys",
            []
        ):

            target_table = fk.get(
                "referenced_table",
                ""
            )

            if not target_table:

                continue

            graph.add_edge(

                source_table,

                target_table
            )

    return graph


# =========================================================
# GENERATE ERD DIAGRAM
# =========================================================

def generate_erd_diagram(
    tables
):

    if not tables:

        return None

    graph = build_graph(
        tables
    )

    output_path = generate_output_path()

    plt.figure(

        figsize=(12, 8)
    )

    pos = nx.spring_layout(
        graph,
        seed=42
    )

    nx.draw(

        graph,

        pos,

        with_labels=True,

        node_size=5000,

        font_size=8
    )

    plt.tight_layout()

    plt.savefig(
        output_path,
        bbox_inches="tight"
    )

    plt.close()

    return output_path