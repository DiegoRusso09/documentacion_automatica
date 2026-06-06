# =========================================================
# FILE: erd_generator.py
# =========================================================

import os
import math
import tempfile

from PIL import (
    Image,
    ImageDraw,
    ImageFont
)


# =========================================================
# FONT
# =========================================================

def get_font(size=16):

    try:

        return ImageFont.truetype(
            "arial.ttf",
            size
        )

    except Exception:

        return ImageFont.load_default()


# =========================================================
# DRAW TABLE
# =========================================================

def draw_table(
    draw,
    x,
    y,
    table
):

    font = get_font(14)

    table_name = table.get(
        "table_name",
        "TABLE"
    )

    columns = table.get(
        "columns",
        []
    )

    pk_columns = set(
        table.get(
            "primary_keys",
            []
        )
    )

    fk_columns = set(

        fk.get(
            "column",
            ""
        )

        for fk in table.get(
            "foreign_keys",
            []
        )
    )

    # =====================================================
    # SHOW ONLY PK/FK
    # =====================================================

    display_columns = []

    for column in columns:

        column_name = column.get(
            "column_name",
            ""
        )

        if (
            column_name in pk_columns
            or
            column_name in fk_columns
        ):

            display_columns.append(
                column
            )

    if not display_columns:

        display_columns.append({

            "column_name":
                "(Sin PK/FK)",

            "data_type":
                ""
        })

    hidden_columns = (

        len(columns)
        -
        len(display_columns)
    )

    # =====================================================
    # SIZE
    # =====================================================

    row_height = 25

    width = 420

    height = (

        50
        +
        len(display_columns)
        * row_height
        +
        30
    )

    # =====================================================
    # HEADER
    # =====================================================

    draw.rectangle(

        [
            (x, y),
            (x + width, y + 40)
        ],

        fill="#D9EAD3",

        outline="black"
    )

    draw.text(

        (
            x + 10,
            y + 10
        ),

        table_name,

        fill="black",

        font=font
    )

    # =====================================================
    # BODY
    # =====================================================

    draw.rectangle(

        [
            (x, y + 40),
            (x + width, y + height)
        ],

        outline="black"
    )

    current_y = y + 50

    for column in display_columns:

        column_name = column.get(
            "column_name",
            ""
        )

        data_type = column.get(
            "data_type",
            ""
        )

        tags = []

        if column_name in pk_columns:

            tags.append(
                "PK"
            )

        if column_name in fk_columns:

            tags.append(
                "FK"
            )

        tag_text = ""

        if tags:

            tag_text = (
                "["
                +
                ",".join(tags)
                +
                "] "
            )

        draw.text(

            (
                x + 10,
                current_y
            ),

            f"{tag_text}{column_name}",

            fill="black",

            font=font
        )

        current_y += row_height

    # =====================================================
    # ADDITIONAL COLUMNS
    # =====================================================

    if hidden_columns > 0:

        draw.text(

            (
                x + 10,
                current_y
            ),

            f"({hidden_columns} columnas adicionales)",

            fill="gray",

            font=font
        )

    return (

        x,
        y,
        width,
        height
    )


# =========================================================
# GENERATE ERD
# =========================================================

def generate_erd_diagram(
    tables
):

    if not tables:

        return None

    temp_dir = tempfile.mkdtemp()

    png_file = os.path.join(
        temp_dir,
        "erd.png"
    )

    table_count = len(
        tables
    )

    columns_per_row = 3

    rows_needed = math.ceil(

        table_count
        /
        columns_per_row
    )

    width = 1800

    height = max(

        1200,

        rows_needed * 320
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

    positions = {}

    # =====================================================
    # GRID LAYOUT
    # =====================================================

    table_width = 460

    table_height = 180

    horizontal_gap = 60

    vertical_gap = 60

    for index, table in enumerate(
        tables
    ):

        col = (
            index
            %
            columns_per_row
        )

        row = (
            index
            //
            columns_per_row
        )

        x = (

            40
            +
            col
            *
            (
                table_width
                +
                horizontal_gap
            )
        )

        y = (

            40
            +
            row
            *
            (
                table_height
                +
                vertical_gap
            )
        )

        box = draw_table(

            draw,

            x,

            y,

            table
        )

        positions[
            table.get(
                "table_name"
            )
        ] = box

    # =====================================================
    # RELATIONSHIPS
    # =====================================================

    for table in tables:

        child_name = table.get(
            "table_name"
        )

        child_box = positions.get(
            child_name
        )

        if not child_box:

            continue

        child_x = (

            child_box[0]
            +
            child_box[2]
            /
            2
        )

        child_y = (

            child_box[1]
            +
            child_box[3]
            /
            2
        )

        for fk in table.get(
            "foreign_keys",
            []
        ):

            parent_name = fk.get(
                "referenced_table"
            )

            parent_box = positions.get(
                parent_name
            )

            if not parent_box:

                continue

            parent_x = (

                parent_box[0]
                +
                parent_box[2]
                /
                2
            )

            parent_y = (

                parent_box[1]
                +
                parent_box[3]
                /
                2
            )

            draw.line(

                [
                    (
                        parent_x,
                        parent_y
                    ),
                    (
                        child_x,
                        child_y
                    )
                ],

                fill="blue",

                width=2
            )

    image.save(
        png_file
    )

    return png_file