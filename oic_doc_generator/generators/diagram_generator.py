# =========================================================
# FILE: diagram_generator.py
# =========================================================

import re
import os
import shutil
import tempfile
import subprocess

from utils.mermaid_utils import (
    sanitize_mermaid_text
)


# =========================================================
# BUILD MERMAID CODE
# =========================================================

def build_mermaid_code(
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

    if integration_type.lower() == "scheduled":

        lines.append(
            "participant SCHEDULER"
        )

        lines.append(
            f"participant FLOW as {endpoint_clean}"
        )

    else:

        lines.append(
            "participant CLIENT"
        )

        lines.append(
            f"participant API as {endpoint_clean}"
        )

    participants = []

    # =====================================================
    # DETECT PARTICIPANTS
    # =====================================================

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

    # =====================================================
    # ADD PARTICIPANTS
    # =====================================================

    for participant in participants:

        lines.append(
            f"participant {participant}"
        )

    # =====================================================
    # START FLOW
    # =====================================================

    if integration_type.lower() == "scheduled":

        lines.append(
            "SCHEDULER->>FLOW: Trigger"
        )

    else:

        lines.append(
            "CLIENT->>API: Request"
        )

    # =====================================================
    # FLOW ACTIONS
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

        if integration_type.lower() == "scheduled":

            lines.append(
                f"FLOW->>{target}: {action}"
            )

            lines.append(
                f"{target}-->>FLOW: Response"
            )

        else:

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

    return "\n".join(lines)


# =========================================================
# GENERATE PNG
# =========================================================

def generate_sequence_diagram_png(
    endpoint_name,
    rows,
    integration_type="REST"
):

    mmdc_path = shutil.which(
        "mmdc"
    )

    # =====================================================
    # WINDOWS FALLBACKS
    # =====================================================

    if not mmdc_path:

        possible_paths = [

            r"C:\Users\LP-KQ-NEORA\AppData\Roaming\npm\mmdc.cmd",

            r"C:\Users\LP-KQ-NEORA\AppData\Roaming\npm\mmdc"

        ]

        for path in possible_paths:

            if os.path.exists(path):

                mmdc_path = path
                break

    if not mmdc_path:

        raise Exception(
            "No se encontró Mermaid CLI (mmdc)"
        )

    # =====================================================
    # TEMP FILES
    # =====================================================

    temp_dir = tempfile.mkdtemp()

    mmd_file = os.path.join(
        temp_dir,
        "diagram.mmd"
    )

    png_file = os.path.join(
        temp_dir,
        "diagram.png"
    )

    # =====================================================
    # MERMAID CODE
    # =====================================================

    mermaid_code = build_mermaid_code(

        endpoint_name,
        rows,
        integration_type

    )

    # =====================================================
    # WRITE FILE
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
    # EXECUTE MERMAID CLI
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
    # VALIDATE
    # =====================================================

    if result.returncode != 0:

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