# =========================================================
# FILE: oic_doc_generator/utils/mermaid_utils.py
# =========================================================

import os
import re
import shutil
import subprocess
import tempfile

import streamlit as st


# =========================================================
# SANITIZE MERMAID TEXT
# =========================================================

def sanitize_mermaid_text(
    text
):

    if not text:

        return "UNKNOWN"

    text = re.sub(

        r'["\'<>]',

        '',

        text
    )

    text = text.replace(
        "-",
        "_"
    )

    text = text.replace(
        " ",
        "_"
    )

    text = text.replace(
        "/",
        "_"
    )

    text = text.replace(
        ".",
        "_"
    )

    return text


# =========================================================
# FIND MMDC
# =========================================================

def find_mmdc():

    mmdc_path = shutil.which(
        "mmdc"
    )

    if mmdc_path:

        return mmdc_path

    possible_paths = [

        r"C:\Users\LP-KQ-NEORA\AppData\Roaming\npm\mmdc.cmd",

        r"C:\Users\LP-KQ-NEORA\AppData\Roaming\npm\mmdc"
    ]

    for path in possible_paths:

        if os.path.exists(
            path
        ):

            return path

    return None


# =========================================================
# GENERATE MERMAID CODE
# =========================================================

def generate_mermaid_code(
    endpoint_name,
    rows,
    integration_type="REST"
):

    lines = []

    lines.append(
        "%%{init: {'theme':'neutral'}}%%"
    )

    lines.append(
        "sequenceDiagram"
    )

    lines.append(
        "autonumber"
    )

    endpoint_clean = sanitize_mermaid_text(
        endpoint_name
    )

    # =====================================================
    # PARTICIPANTS
    # =====================================================

    if integration_type.lower() != "scheduled":

        lines.append(
            "participant CLIENT"
        )

    lines.append(
        f"participant API as {endpoint_clean}"
    )

    participants = []

    for row in rows[1:]:

        desc = row.get(
            "Descripción de la Acción",
            ""
        )

        tipo_match = re.search(

            r'De tipo ([^,\.]+)',

            desc
        )

        participant = "SYSTEM"

        if tipo_match:

            participant = sanitize_mermaid_text(
                tipo_match.group(1)
            )

        if participant not in participants:

            participants.append(
                participant
            )

    for participant in participants:

        lines.append(
            f"participant {participant}"
        )

    # =====================================================
    # START FLOW
    # =====================================================

    if integration_type.lower() != "scheduled":

        lines.append(
            "CLIENT->>API: Request"
        )

    else:

        lines.append(
            "Note over API: Scheduled Execution"
        )

    # =====================================================
    # ACTIONS
    # =====================================================

    for row in rows[1:]:

        action = sanitize_mermaid_text(

            row.get(
                "Nombre Acción",
                "ACTION"
            )
        )

        desc = row.get(
            "Descripción de la Acción",
            ""
        )

        tipo_match = re.search(

            r'De tipo ([^,\.]+)',

            desc
        )

        target = "SYSTEM"

        if tipo_match:

            target = sanitize_mermaid_text(
                tipo_match.group(1)
            )

        lines.append(
            f"API->>{target}: {action}"
        )

        lines.append(
            f"{target}-->>API: Response"
        )

    # =====================================================
    # END FLOW
    # =====================================================

    if integration_type.lower() != "scheduled":

        lines.append(
            "API-->>CLIENT: Response"
        )

    return "\n".join(
        lines
    )


# =========================================================
# GENERATE SEQUENCE DIAGRAM PNG
# =========================================================

def generate_sequence_diagram_png(

    endpoint_name,

    rows,

    integration_type="REST"
):

    mmdc_path = find_mmdc()

    if not mmdc_path:

        raise Exception(
            "No se encontró Mermaid CLI (mmdc)"
        )

    temp_dir = tempfile.mkdtemp()

    mmd_file = os.path.join(

        temp_dir,

        "diagram.mmd"
    )

    png_file = os.path.join(

        temp_dir,

        "diagram.png"
    )

    mermaid_code = generate_mermaid_code(

        endpoint_name,

        rows,

        integration_type
    )

    # =====================================================
    # SHOW CODE IN STREAMLIT
    # =====================================================

    st.code(
        mermaid_code,
        language="text"
    )

    # =====================================================
    # WRITE MMD FILE
    # =====================================================

    with open(

        mmd_file,

        "w",

        encoding="utf-8"

    ) as f:

        f.write(
            mermaid_code
        )

    # =====================================================
    # EXECUTE MMDC
    # =====================================================

    result = subprocess.run(

        [

            mmdc_path,

            "-i",
            mmd_file,

            "-o",
            png_file,

            "-t",
            "neutral",

            "-b",
            "white",

            "-s",
            "2"
        ],

        capture_output=True,

        text=True
    )

    # =====================================================
    # VALIDATE RESULT
    # =====================================================

    if result.returncode != 0:

        st.error(
            result.stderr
        )

        raise Exception(
            result.stderr
        )

    if not os.path.exists(
        png_file
    ):

        raise Exception(
            "Mermaid no generó PNG"
        )

    return png_file