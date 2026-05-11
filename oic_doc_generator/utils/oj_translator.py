# =========================================================
# FILE:
# oic_doc_generator/utils/oj_translator.py
# =========================================================

import json
import re

from bs4 import BeautifulSoup


# =========================================================
# TRANSLATE COMPLETE HTML
# =========================================================

def translate_oj_html(
    html
):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    # =====================================================
    # REMOVE DIALOGS
    # =====================================================

    remove_oj_dialogs(
        soup
    )

    # =====================================================
    # TRANSLATE COMPONENTS
    # =====================================================

    translate_oj_button(
        soup
    )

    translate_oj_input_text(
        soup
    )

    translate_oj_input_password(
        soup
    )

    translate_oj_input_number(
        soup
    )

    translate_oj_text_area(
        soup
    )

    translate_oj_select_single(
        soup
    )

    translate_oj_combobox_one(
        soup
    )

    translate_oj_table(
        soup
    )

    translate_oj_form_layout(
        soup
    )

    translate_oj_flex(
        soup
    )

    translate_oj_label(
        soup
    )

    translate_oj_bind_text(
        soup
    )

    translate_typography_classes(
        soup
    )

    move_footer_to_bottom(
        soup
    )

    return str(
        soup
    )


# =========================================================
# BASE INPUT STYLE
# =========================================================

BASE_INPUT_STYLE = """
width:100%;
max-width:100%;
min-width:0;
padding:8px;
border:1px solid #cfcfcf;
border-radius:4px;
background:white;
box-sizing:border-box;
min-height:34px;
font-size:13px;
"""


# =========================================================
# EXTRACT IMAGE SRC
# =========================================================

def extract_image_src(
    img_tag
):

    if not img_tag:

        return None

    attrs = [

        "src",

        ":src",

        "data-src"
    ]

    for attr in attrs:

        value = img_tag.get(
            attr
        )

        if not value:

            continue

        match = re.search(

            r"resources/images/[^\"'\]]+",

            value
        )

        if match:

            return match.group(
                0
            )

    return None


# =========================================================
# BUTTON
# =========================================================

def translate_oj_button(
    soup
):

    buttons = soup.find_all(
        "oj-button"
    )

    for tag in buttons:

        button = soup.new_tag(
            "button"
        )

        button["style"] = """
        display:inline-flex;
        align-items:center;
        justify-content:center;
        gap:6px;
        min-height:36px;
        min-width:36px;
        padding:8px 12px;
        border:1px solid #cccccc;
        border-radius:4px;
        background:#f5f5f5;
        cursor:pointer;
        box-sizing:border-box;
        """

        # =================================================
        # ICON
        # =================================================

        img = tag.find(
            "img"
        )

        if img:

            src = extract_image_src(
                img
            )

            if src:

                icon = soup.new_tag(
                    "img"
                )

                icon["src"] = src

                icon["style"] = """
                width:16px;
                height:16px;
                object-fit:contain;
                display:block;
                """

                button.append(
                    icon
                )

        # =================================================
        # LABEL
        # =================================================

        else:

            label = tag.get(
                "label",
                "Button"
            )

            span = soup.new_tag(
                "span"
            )

            span.string = label

            button.append(
                span
            )

        tag.replace_with(
            button
        )


# =========================================================
# INPUT TEXT
# =========================================================

def translate_oj_input_text(
    soup
):

    tags = soup.find_all(
        "oj-input-text"
    )

    for tag in tags:

        input_tag = soup.new_tag(
            "input"
        )

        input_tag["type"] = "text"

        input_tag["style"] = (
            BASE_INPUT_STYLE
        )

        tag.replace_with(
            input_tag
        )


# =========================================================
# INPUT PASSWORD
# =========================================================

def translate_oj_input_password(
    soup
):

    tags = soup.find_all(
        "oj-input-password"
    )

    for tag in tags:

        input_tag = soup.new_tag(
            "input"
        )

        input_tag["type"] = "password"

        input_tag["style"] = (
            BASE_INPUT_STYLE
        )

        tag.replace_with(
            input_tag
        )


# =========================================================
# INPUT NUMBER
# =========================================================

def translate_oj_input_number(
    soup
):

    tags = soup.find_all(
        "oj-input-number"
    )

    for tag in tags:

        input_tag = soup.new_tag(
            "input"
        )

        input_tag["type"] = "number"

        input_tag["style"] = (
            BASE_INPUT_STYLE
        )

        tag.replace_with(
            input_tag
        )


# =========================================================
# TEXT AREA
# =========================================================

def translate_oj_text_area(
    soup
):

    tags = soup.find_all(
        "oj-text-area"
    )

    for tag in tags:

        textarea = soup.new_tag(
            "textarea"
        )

        textarea["style"] = """
        width:100%;
        min-height:120px;
        padding:8px;
        border:1px solid #cfcfcf;
        border-radius:4px;
        box-sizing:border-box;
        resize:none;
        font-size:13px;
        """

        tag.replace_with(
            textarea
        )


# =========================================================
# SELECT SINGLE
# =========================================================

def translate_oj_select_single(
    soup
):

    tags = soup.find_all(
        "oj-select-single"
    )

    for tag in tags:

        select = soup.new_tag(
            "select"
        )

        select["style"] = (
            BASE_INPUT_STYLE
        )

        option = soup.new_tag(
            "option"
        )

        option.string = "Seleccione"

        select.append(
            option
        )

        tag.replace_with(
            select
        )


# =========================================================
# COMBOBOX ONE
# =========================================================

def translate_oj_combobox_one(
    soup
):

    tags = soup.find_all(
        "oj-combobox-one"
    )

    for tag in tags:

        select = soup.new_tag(
            "select"
        )

        select["style"] = (
            BASE_INPUT_STYLE
        )

        option = soup.new_tag(
            "option"
        )

        option.string = "Seleccione"

        select.append(
            option
        )

        tag.replace_with(
            select
        )


# =========================================================
# TABLE
# =========================================================

def translate_oj_table(
    soup
):

    tables = soup.find_all(
        "oj-table"
    )

    for tag in tables:

        table = soup.new_tag(
            "table"
        )

        table["style"] = """
        width:100%;
        border-collapse:collapse;
        margin-top:12px;
        margin-bottom:16px;
        font-size:12px;
        background:white;
        """

        thead = soup.new_tag(
            "thead"
        )

        tr = soup.new_tag(
            "tr"
        )

        columns_attr = tag.get(
            "columns",
            "[]"
        )

        try:

            columns = json.loads(
                columns_attr
            )

        except:

            columns = []

        for column in columns:

            th = soup.new_tag(
                "th"
            )

            th.string = column.get(
                "headerText",
                "Columna"
            )

            th["style"] = """
            background:#f3f3f3;
            border:1px solid #d8d8d8;
            padding:8px;
            text-align:left;
            white-space:nowrap;
            font-weight:bold;
            """

            tr.append(
                th
            )

        thead.append(
            tr
        )

        table.append(
            thead
        )

        tbody = soup.new_tag(
            "tbody"
        )

        empty_row = soup.new_tag(
            "tr"
        )

        for _ in columns:

            td = soup.new_tag(
                "td"
            )

            td.string = ""

            td["style"] = """
            border:1px solid #d8d8d8;
            padding:8px;
            height:30px;
            """

            empty_row.append(
                td
            )

        tbody.append(
            empty_row
        )

        table.append(
            tbody
        )

        tag.replace_with(
            table
        )


# =========================================================
# FORM LAYOUT
# =========================================================

def translate_oj_form_layout(
    soup
):

    layouts = soup.find_all(
        "oj-form-layout"
    )

    for tag in layouts:

        columns = tag.get(
            "columns",
            "1"
        )

        try:

            columns = int(
                columns
            )

        except:

            columns = 1

        tag.name = "div"

        tag["style"] = f"""
        display:grid;
        grid-template-columns:
            repeat(
                {columns},
                minmax(220px, 1fr)
            );
        gap:16px;
        width:100%;
        margin-bottom:16px;
        align-items:start;
        box-sizing:border-box;
        """

        children = tag.find_all(
            recursive=False
        )

        for child in children:

            current = child.get(
                "style",
                ""
            )

            child["style"] = (
                current
                +
                """
                width:100%;
                min-width:0;
                box-sizing:border-box;
                """
            )


# =========================================================
# FLEX
# =========================================================

def translate_oj_flex(
    soup
):

    flex_tags = soup.find_all(
        class_="oj-flex"
    )

    for tag in flex_tags:

        classes = tag.get(
            "class",
            []
        )

        direction = "row"

        if (
            "oj-sm-flex-direction-column"
            in classes
        ):

            direction = "column"

        current_style = tag.get(
            "style",
            ""
        )

        tag["style"] = (
            current_style
            +
            f"""
            display:flex;
            flex-direction:{direction};
            gap:16px;
            flex-wrap:wrap;
            width:100%;
            align-items:flex-start;
            box-sizing:border-box;
            """
        )


# =========================================================
# LABEL
# =========================================================

def translate_oj_label(
    soup
):

    labels = soup.find_all(
        "oj-label"
    )

    for tag in labels:

        label = soup.new_tag(
            "label"
        )

        label.string = tag.text

        label["style"] = """
        display:block;
        margin-bottom:4px;
        font-size:13px;
        font-weight:normal;
        """

        tag.replace_with(
            label
        )


# =========================================================
# BIND TEXT
# =========================================================

def translate_oj_bind_text(
    soup
):

    tags = soup.find_all(
        "oj-bind-text"
    )

    for tag in tags:

        span = soup.new_tag(
            "span"
        )

        span.string = tag.get(
            "value",
            "Texto"
        )

        tag.replace_with(
            span
        )


# =========================================================
# TYPOGRAPHY
# =========================================================

def translate_typography_classes(
    soup
):

    tags = soup.find_all(
        True
    )

    for tag in tags:

        classes = tag.get(
            "class",
            []
        )

        styles = []

        if (
            "oj-typography-bold"
            in classes
        ):

            styles.append(
                "font-weight:bold;"
            )

        if (
            "oj-underline"
            in classes
        ):

            styles.append(
                "text-decoration:underline;"
            )

        if styles:

            current = tag.get(
                "style",
                ""
            )

            tag["style"] = (
                current
                + ";"
                + " ".join(styles)
            )


# =========================================================
# REMOVE DIALOGS
# =========================================================

def remove_oj_dialogs(
    soup
):

    dialogs = soup.find_all(
        "oj-dialog"
    )

    for dialog in dialogs:

        dialog.decompose()


# =========================================================
# FOOTER
# =========================================================

def move_footer_to_bottom(
    soup
):

    footers = soup.find_all(
        "footer"
    )

    for footer in footers:

        classes = footer.get(
            "class",
            []
        )

        if (
            "oj-web-applayout-footer"
            in classes
        ):

            footer.extract()

            soup.append(
                footer
            )