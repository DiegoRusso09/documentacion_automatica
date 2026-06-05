# =========================================================
# mermaid_utils.py
# =========================================================

import os
import re
import shutil
import tempfile
import subprocess


# =========================================================
# SANITIZE MERMAID TEXT
# =========================================================

def sanitize_mermaid_text(text):

    if not text:
        return "UNKNOWN"

    text = str(text)

    text = re.sub(
        r'["\'<>]',
        '',
        text
    )

    text = text.replace("-", "_")
    text = text.replace(" ", "_")
    text = text.replace("/", "_")
    text = text.replace("\\", "_")
    text = text.replace(".", "_")
    text = text.replace(":", "_")

    text = re.sub(
        r'[^a-zA-Z0-9_]',
        '',
        text
    )

    if re.match(r'^\d', text):

        text = f"N_{text}"

    return text


# =========================================================
# FIND MMDC
# =========================================================

def find_mmdc():

    import os
    import shutil

    candidates = [

        shutil.which("mmdc"),

        "/usr/local/bin/mmdc",

        "/usr/bin/mmdc",

        "/home/adminuser/.npm-global/bin/mmdc",

        "/home/adminuser/venv/bin/mmdc"
    ]

    for candidate in candidates:

        if candidate and os.path.exists(
            candidate
        ):

            return candidate

    raise Exception(
        f"""
Mermaid CLI no encontrado.

PATH:
{os.environ.get('PATH')}
"""
    )

# =========================================================
# BUILD MERMAID CODE
# =========================================================

def build_mermaid_code(
    endpoint_name,
    rows,
    integration_type="REQUEST"
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

    if integration_type.upper() == "SCHEDULED":

        lines.append(
            "participant SCHEDULER"
        )

        lines.append(
            f"participant API as {endpoint_clean}"
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
    # DETECT TARGET TYPE
    # =====================================================

    def detect_target(desc):

        desc_lower = desc.lower()

        # ================================================
        # INTEGRATION
        # ================================================

        if "integración" in desc_lower:

            return "INTEGRATION"

        # ================================================
        # CONNECTION TYPES
        # ================================================

        known_types = [

            "FTP",
            "REST",
            "SOAP",
            "DBAAS",
            "ERP",
            "STAGEFILE"
        ]

        for conn_type in known_types:

            if conn_type.lower() in desc_lower:

                return conn_type

        # ================================================
        # INTERNAL ACTIONS
        # ================================================

        internal_keywords = [

            "assignment",
            "switch",
            "for",
            "while",
            "scope"
        ]

        for keyword in internal_keywords:

            if keyword in desc_lower:

                return "SYSTEM"

        return "SYSTEM"

    # =====================================================
    # PARTICIPANTS
    # =====================================================

    for row in rows[1:]:

        desc = row.get(
            "Descripción de la Acción",
            ""
        )

        participant = detect_target(
            desc
        )

        participant = sanitize_mermaid_text(
            participant
        )

        if participant not in participants:

            participants.append(
                participant
            )

    # =====================================================
    # APPEND PARTICIPANTS
    # =====================================================

    for participant in participants:

        lines.append(
            f"participant {participant}"
        )

    # =====================================================
    # START FLOW
    # =====================================================

    if integration_type.upper() == "SCHEDULED":

        lines.append(
            "SCHEDULER->>API: Trigger"
        )

    else:

        lines.append(
            "CLIENT->>API: Request"
        )

    # =====================================================
    # ACTIONS
    # =====================================================

    for row in rows[1:]:

        action = row.get(
            "Nombre Acción",
            "ACTION"
        )

        action = sanitize_mermaid_text(
            action
        )

        desc = row.get(
            "Descripción de la Acción",
            ""
        )

        target = detect_target(
            desc
        )

        target = sanitize_mermaid_text(
            target
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

    if integration_type.upper() != "SCHEDULED":

        lines.append(
            "API-->>CLIENT: Response"
        )

    return "\n".join(lines)

# =========================================================
# GENERATE MERMAID PNG
# =========================================================

def generate_sequence_diagram_png(
    endpoint_name,
    rows,
    integration_type="REQUEST"
):

    mmdc_path = find_mmdc()

    if not mmdc_path:

        raise Exception(
            "No se encontró Mermaid CLI (mmdc). "
            "Instalar con: npm install -g @mermaid-js/mermaid-cli"
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

    mermaid_code = build_mermaid_code(
        endpoint_name,
        rows,
        integration_type
    )

    with open(
        mmd_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            mermaid_code
        )

    env = os.environ.copy()

    env["PUPPETEER_EXECUTABLE_PATH"] = (
        "/opt/render/.cache/ms-playwright/"
        "chromium_headless_shell-1223/"
        "chrome-headless-shell-linux64/"
        "chrome-headless-shell"
    )

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
            "white"
        ],

        capture_output=True,

        text=True,

        env=env
    )

    if result.returncode != 0:

        raise Exception(
            f"Error Mermaid:\n{result.stderr}"
        )

    if not os.path.exists(
        png_file
    ):

        raise Exception(
            "Mermaid no generó PNG"
        )

    return png_file


# =========================================================
# GENERATE MERMAID TXT
# =========================================================

def generate_mermaid_txt(
    endpoint_name,
    rows,
    integration_type="REQUEST"
):

    temp_dir = tempfile.mkdtemp()

    txt_file = os.path.join(
        temp_dir,
        "diagram.txt"
    )

    mermaid_code = build_mermaid_code(
        endpoint_name,
        rows,
        integration_type
    )

    with open(
        txt_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            mermaid_code
        )

    return txt_file