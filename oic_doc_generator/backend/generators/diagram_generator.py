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
# DRAW BOX
# =========================================================

def draw_box(
    draw,
    x,
    y,
    width,
    height,
    text,
    fill_color="#D9EAD3"
):

    draw.rectangle(

        [
            (x, y),
            (x + width, y + height)
        ],

        outline="black",
        fill=fill_color,
        width=2
    )

    font = get_font(16)

    draw.multiline_text(

        (
            x + 10,
            y + 12
        ),

        text,

        fill="black",

        font=font
    )


# =========================================================
# DRAW ARROW
# =========================================================

def draw_arrow(
    draw,
    x1,
    y1,
    x2,
    y2
):

    draw.line(

        [
            (x1, y1),
            (x2, y2)
        ],

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

    # =====================================================
    # BUILD STEPS
    # =====================================================

    steps = []

    if integration_type.lower() == "scheduled":

        steps.append(
            "SCHEDULER"
        )

    else:

        steps.append(
            "CLIENT"
        )

    steps.append(
        sanitize_text(
            endpoint_name
        )
    )

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

        steps.append(
            f"{target}\n{action}"
        )

    if integration_type.lower() != "scheduled":

        steps.append(
            "CLIENT"
        )

    # =====================================================
    # IMAGE SIZE
    # =====================================================

    box_width = 260
    box_height = 70

    margin_x = 40
    margin_y = 40

    vertical_gap = 60

    width = 900

    height = (

        len(steps)
        * (box_height + vertical_gap)

        + 100
    )

    image = Image.new(

        "RGB",

        (
            width,
            height
        ),

        "white"
    )

    draw = ImageDraw.Draw(
        image
    )

    # =====================================================
    # DRAW FLOW
    # =====================================================

    center_x = (
        width // 2
    )

    current_y = margin_y

    previous_center = None

    for step in steps:

        x = center_x - (
            box_width // 2
        )

        draw_box(

            draw,

            x,

            current_y,

            box_width,

            box_height,

            step
        )

        current_center = (

            center_x,

            current_y +
            box_height
        )

        if previous_center:

            draw_arrow(

                draw,

                previous_center[0],

                previous_center[1],

                current_center[0],

                current_y
            )

        previous_center = current_center

        current_y += (

            box_height +
            vertical_gap
        )

    # =====================================================
    # SAVE
    # =====================================================

    image.save(
        png_file
    )

    if not os.path.exists(
        png_file
    ):

        raise Exception(
            "No se pudo generar el diagrama PNG"
        )

    return png_file