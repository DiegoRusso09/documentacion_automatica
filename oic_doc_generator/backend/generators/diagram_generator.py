# =========================================================
# FILE: diagram_generator.py
# =========================================================

import os
import re
import tempfile

from PIL import (
    Image,
    ImageDraw,
    ImageFont
)


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
# DETECT SYSTEM
# =========================================================

def detect_system(description):

    if not description:

        return None

    text = description.lower()

    if "dbaas" in text:

        return "DBAAS"

    if "soap" in text:

        return "SOAP"

    if "ftp" in text:

        return "FTP"

    if "rest" in text:

        return "REST"

    if "erp" in text:

        return "ERP"

    if "stagefile" in text:

        return "STAGEFILE"

    return None

# =========================================================
# LOAD FONT
# =========================================================

def get_font(size=18):

    try:

        return ImageFont.truetype(
            "arial.ttf",
            size
        )

    except Exception:

        return ImageFont.load_default()

# =========================================================
# DRAW ARROW
# =========================================================

def draw_arrow(
    draw,
    x1,
    y1,
    x2,
    y2,
    label=None
):

    draw.line(
        [(x1, y1), (x2, y2)],
        fill="black",
        width=2
    )

    draw.polygon(
        [
            (x2, y2),
            (x2 - 10, y2 - 5),
            (x2 - 10, y2 + 5)
        ],
        fill="black"
    )

    if label:

        font = get_font(14)

        draw.text(
            (
                (x1 + x2) / 2 - 30,
                y1 - 20
            ),
            label,
            fill="black",
            font=font
        )


# =========================================================
# DRAW LIFELINE
# =========================================================

def draw_lifeline(
    draw,
    x,
    title,
    image_height
):

    font = get_font(16)

    draw.rectangle(
        [
            (x - 60, 20),
            (x + 60, 60)
        ],
        outline="black",
        fill="#D9EAD3",
        width=2
    )

    draw.text(
        (x - 45, 32),
        title,
        fill="black",
        font=font
    )

    draw.line(
        [
            (x, 60),
            (x, image_height - 40)
        ],
        fill="gray",
        width=1
    )

    # =========================================================
# GENERATE UML SEQUENCE PNG
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

    participants = []

    if integration_type.lower() == "scheduled":

        participants.append(
            "SCHEDULER"
        )

    else:

        participants.append(
            "CLIENT"
        )

    participants.append(
        "API"
    )

    for row in rows[1:]:

        system = detect_system(

            row.get(
                "Descripción de la Acción",
                ""
            )
        )

        if (
            system
            and system not in participants
        ):

            participants.append(
                system
            )

    width = max(

        1200,

        len(participants) * 220
    )

    height = max(

        800,

        len(rows) * 80 + 200
    )

    image = Image.new(

        "RGB",

        (width, height),

        "white"
    )

    draw = ImageDraw.Draw(
        image
    )

    positions = {}

    current_x = 120

    for participant in participants:

        positions[participant] = current_x

        draw_lifeline(

            draw,

            current_x,

            participant,

            height
        )

        current_x += 220

    current_y = 120

    if integration_type.lower() == "scheduled":

        draw_arrow(

            draw,

            positions["SCHEDULER"],

            current_y,

            positions["API"],

            current_y,

            "Trigger"
        )

    else:

        draw_arrow(

            draw,

            positions["CLIENT"],

            current_y,

            positions["API"],

            current_y,

            "Request"
        )

    current_y += 80

    for row in rows[1:]:

        action = sanitize_text(

            row.get(
                "Nombre Acción",
                "ACTION"
            )
        )

        system = detect_system(

            row.get(
                "Descripción de la Acción",
                ""
            )
        )

        if not system:

            continue

        draw_arrow(

            draw,

            positions["API"],

            current_y,

            positions[system],

            current_y,

            action
        )

        current_y += 50

        draw_arrow(

            draw,

            positions[system],

            current_y,

            positions["API"],

            current_y,

            "Response"
        )

        current_y += 50

    if integration_type.lower() != "scheduled":

        draw_arrow(

            draw,

            positions["API"],

            current_y,

            positions["CLIENT"],

            current_y,

            "Response"
        )

    image.save(
        png_file
    )

    return png_file