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

    remove_templates(
        soup
    )

    flatten_bind_if(
        soup
    )

    flatten_bind_for_each(
        soup
    )

    remove_oj_options(
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

    translate_oj_input_date(
        soup
    )

    translate_oj_input_date_time(
        soup
    )

    translate_oj_switch(
        soup
    )

    translate_oj_layout_classes(
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

    translate_oj_flex_item(
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
# REMOVE OJ OPTIONS
# =========================================================

def remove_oj_options(
    soup
):

    options = soup.find_all(
        "oj-option"
    )

    for option in options:

        option.decompose()

# =========================================================
# PRESERVE ORIGINAL ATTRIBUTES
# =========================================================

def preserve_original_attributes(
    original_tag,
    new_tag
):

    original_classes = original_tag.get(
        "class"
    )

    if original_classes:

        new_tag["class"] = original_classes

    original_style = original_tag.get(
        "style"
    )

    if original_style:

        current_style = new_tag.get(
            "style",
            ""
        )

        # ==========================================
        # CLEAN PROBLEMATIC PADDINGS
        # ==========================================

        cleaned_style = original_style

        if new_tag.name == "button":

            # remove huge paddings
            cleaned_style = re.sub(
                r"padding-top\s*:\s*\d+px\s*;",
                "",
                cleaned_style,
                flags=re.IGNORECASE
            )

            cleaned_style = re.sub(
                r"min-width\s*:\s*1[0-9]{3}px\s*;",
                "",
                cleaned_style,
                flags=re.IGNORECASE
            )

            cleaned_style = re.sub(
                r"padding-bottom\s*:\s*\d+px\s*;",
                "",
                cleaned_style,
                flags=re.IGNORECASE
            )

        new_tag["style"] = (
            current_style
            + ";"
            + cleaned_style
        )


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

import re


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

        # =================================================
        # ORIGINAL STYLE
        # =================================================

        original_style = tag.get(
            "style",
            ""
        )

        cleaned_style = original_style

        # =================================================
        # FIX ORACLE VB POSITIONING HACKS
        # =================================================
        # Oracle VB sometimes uses huge paddings
        # to visually move buttons instead of
        # actually resizing them.
        #
        # Example:
        # padding-top:216px;
        #
        # In browsers this works visually because
        # Oracle JET internal structure absorbs it,
        # but in our translated renderer it causes
        # gigantic buttons.
        #
        # So we convert huge vertical paddings
        # into margins.
        # =================================================

        padding_top_match = re.search(
            r'padding-top\s*:\s*(\d+)px',
            cleaned_style,
            re.IGNORECASE
        )

        if padding_top_match:

            padding_value = int(
                padding_top_match.group(1)
            )

            if padding_value >= 40:

                cleaned_style = re.sub(
                    r'padding-top\s*:\s*\d+px\s*;?',
                    f'margin-top:{padding_value}px;',
                    cleaned_style,
                    flags=re.IGNORECASE
                )

        padding_bottom_match = re.search(
            r'padding-bottom\s*:\s*(\d+)px',
            cleaned_style,
            re.IGNORECASE
        )

        if padding_bottom_match:

            padding_value = int(
                padding_bottom_match.group(1)
            )

            if padding_value >= 40:

                cleaned_style = re.sub(
                    r'padding-bottom\s*:\s*\d+px\s*;?',
                    f'margin-bottom:{padding_value}px;',
                    cleaned_style,
                    flags=re.IGNORECASE
                )

        # =================================================
        # BASE BUTTON STYLE
        # =================================================

        base_style = """
        display:inline-flex;
        align-items:center;
        justify-content:center;
        gap:6px;

        width:auto;
        max-width:max-content;
        flex:none;
        align-self:flex-start;

        min-height:36px;
        min-width:36px;

        padding:8px 12px;

        border:1px solid #cccccc;
        border-radius:4px;

        background:#f5f5f5;

        cursor:pointer;

        box-sizing:border-box;

        white-space:nowrap;
        """

        # =================================================
        # MERGE STYLES
        # =================================================

        if cleaned_style:

            button["style"] = (
                base_style
                +
                cleaned_style
            )

        else:

            button["style"] = base_style

        preserve_original_attributes(
            tag,
            button
        )

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
                flex:none;
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

            span["style"] = """
            white-space:nowrap;
            """

            button.append(
                span
            )

        # =================================================
        # REPLACE
        # =================================================

        tag.replace_with(
            button
        )


# =========================================================
# SWITCH
# =========================================================

def translate_oj_switch(
    soup
):

    tags = soup.find_all(
        "oj-switch"
    )

    for tag in tags:

        wrapper = soup.new_tag(
            "div"
        )

        wrapper["style"] = """
        display:flex;
        align-items:center;
        min-height:34px;
        """

        input_tag = soup.new_tag(
            "input"
        )

        input_tag["type"] = "checkbox"

        input_tag["style"] = """
        width:18px;
        height:18px;
        cursor:pointer;
        """

        label_hint = tag.get(
            "label-hint"
        )

        if label_hint:

            wrapper[
                "data-label-hint"
            ] = label_hint

        preserve_original_attributes(
            tag,
            input_tag
        )

        wrapper.append(
            input_tag
        )

        tag.replace_with(
            wrapper
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

        label_hint = tag.get(
            "label-hint"
        )

        if label_hint:

            input_tag[
                "data-label-hint"
            ] = label_hint

        preserve_original_attributes(
            tag,
            input_tag
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

        preserve_original_attributes(
            tag,
            input_tag
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

        label_hint = tag.get(
            "label-hint"
        )

        if label_hint:

            input_tag[
                "data-label-hint"
            ] = label_hint

        preserve_original_attributes(
            tag,
            input_tag
        )

        tag.replace_with(
            input_tag
        )


# =========================================================
# INPUT DATE
# =========================================================

def translate_oj_input_date(
    soup
):

    tags = soup.find_all(
        "oj-input-date"
    )

    for tag in tags:

        input_tag = soup.new_tag(
            "input"
        )

        input_tag["type"] = "date"

        input_tag["style"] = (
            BASE_INPUT_STYLE
        )

        label_hint = tag.get(
            "label-hint"
        )

        if label_hint:

            input_tag[
                "data-label-hint"
            ] = label_hint

        preserve_original_attributes(
            tag,
            input_tag
        )

        tag.replace_with(
            input_tag
        )


# =========================================================
# INPUT DATE TIME
# =========================================================

def translate_oj_input_date_time(
    soup
):

    tags = soup.find_all(
        "oj-input-date-time"
    )

    for tag in tags:

        input_tag = soup.new_tag(
            "input"
        )

        input_tag["type"] = "datetime-local"

        input_tag["style"] = (
            BASE_INPUT_STYLE
        )

        label_hint = tag.get(
            "label-hint"
        )

        if label_hint:

            input_tag[
                "data-label-hint"
            ] = label_hint

        preserve_original_attributes(
            tag,
            input_tag
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

        preserve_original_attributes(
            tag,
            textarea
        )

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

        label_hint = tag.get(
            "label-hint"
        )

        if label_hint:

            select[
                "data-label-hint"
            ] = label_hint

        preserve_original_attributes(
            tag,
            select
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

        label_hint = tag.get(
            "label-hint"
        )

        if label_hint:

            select[
                "data-label-hint"
            ] = label_hint

        preserve_original_attributes(
            tag,
            select
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
        table-layout:auto;
        overflow:hidden;
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

        wrapper = soup.new_tag(
            "div"
        )

        wrapper["style"] = """
        width:100%;
        overflow-x:auto;
        box-sizing:border-box;
        """

        wrapper.append(
            table
        )

        tag.replace_with(
            wrapper
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

        label_width = tag.get(
            "label-width",
            "30%"
        )

        try:

            columns = int(columns)

        except:

            columns = 1

        container = soup.new_tag(
            "div"
        )

        container["class"] = [
            "vb-form-layout"
        ]

        container["style"] = f"""
        display:grid;
        grid-template-columns:
            repeat(
                {columns},
                minmax(320px, 1fr)
            );
        column-gap:24px;
        row-gap:14px;
        width:100%;
        align-items:start;
        box-sizing:border-box;
        margin-bottom:20px;
        """

        children = tag.find_all(
            recursive=False
        )

        i = 0

        while i < len(children):

            child = children[i]

            # =================================================
            # CASE 1:
            # oj-label + component
            # =================================================

            if child.name == "oj-label":

                field = soup.new_tag(
                    "div"
                )

                field["class"] = [
                    "vb-form-field"
                ]

                field["style"] = """
                display:flex;
                align-items:center;
                gap:12px;
                width:100%;
                min-width:0;
                box-sizing:border-box;
                """

                label = soup.new_tag(
                    "label"
                )

                label.string = child.text.strip()

                label["style"] = f"""
                width:{label_width};
                min-width:180px;
                flex-shrink:0;
                font-size:13px;
                """

                field.append(
                    label
                )

                if i + 1 < len(children):

                    next_child = children[
                        i + 1
                    ]

                    control_wrapper = soup.new_tag(
                        "div"
                    )

                    control_wrapper["style"] = """
                    flex:1 1 auto;
                    min-width:180px;
                    """

                    control_wrapper.append(
                        next_child
                    )

                    field.append(
                        control_wrapper
                    )

                    i += 1

                container.append(
                    field
                )

            # =================================================
            # CASE 2:
            # label-hint
            # =================================================

            else:

                label_hint = (
                    child.get(
                        "data-label-hint"
                    )
                    or
                    child.get(
                        "label-hint"
                    )
                )

                if label_hint:

                    field = soup.new_tag(
                        "div"
                    )

                    field["class"] = [
                        "vb-form-field"
                    ]

                    field["style"] = """
                    display:flex;
                    align-items:center;
                    gap:12px;
                    width:100%;
                    min-width:0;
                    box-sizing:border-box;
                    """

                    label = soup.new_tag(
                        "label"
                    )

                    label.string = label_hint

                    label["style"] = f"""
                    width:{label_width};
                    min-width:180px;
                    flex-shrink:0;
                    font-size:13px;
                    """

                    field.append(
                        label
                    )

                    control_wrapper = soup.new_tag(
                        "div"
                    )

                    control_wrapper["style"] = """
                    flex:1 1 auto;
                    min-width:180px;
                    """

                    control_wrapper.append(
                        child
                    )

                    field.append(
                        control_wrapper
                    )

                    container.append(
                        field
                    )

                else:

                    container.append(
                        child
                    )

            i += 1

        tag.replace_with(
            container
        )


# =========================================================
# ORACLE JET LAYOUT / GRID CLASSES
# =========================================================

def translate_oj_layout_classes(
    soup
):

    all_tags = soup.find_all(
        True
    )

    for tag in all_tags:

        classes = tag.get(
            "class",
            []
        )

        if not classes:

            continue

        styles = []

        # =================================================
        # FLEX ITEM
        # =================================================

        if "oj-flex-item" in classes:

            styles.append(
                "box-sizing:border-box;"
            )

        # =================================================
        # FLEX INITIAL
        # =================================================

        if "oj-sm-flex-initial" in classes:

            styles.append(
                "flex-grow:0;"
            )

            styles.append(
                "flex-shrink:1;"
            )

        # =================================================
        # WIDTH GRID SYSTEM
        # =================================================

        grid_map = {

            "oj-sm-1":  "8.333%",
            "oj-sm-2":  "16.666%",
            "oj-sm-3":  "25%",
            "oj-sm-4":  "33.333%",
            "oj-sm-5":  "41.666%",
            "oj-sm-6":  "50%",
            "oj-sm-7":  "58.333%",
            "oj-sm-8":  "66.666%",
            "oj-sm-9":  "75%",
            "oj-sm-10": "83.333%",
            "oj-sm-11": "91.666%",
            "oj-sm-12": "100%",

            "oj-md-1":  "8.333%",
            "oj-md-2":  "16.666%",
            "oj-md-3":  "25%",
            "oj-md-4":  "33.333%",
            "oj-md-5":  "41.666%",
            "oj-md-6":  "50%",
            "oj-md-7":  "58.333%",
            "oj-md-8":  "66.666%",
            "oj-md-9":  "75%",
            "oj-md-10": "83.333%",
            "oj-md-11": "91.666%",
            "oj-md-12": "100%"
        }

        applied_width = None

        for class_name in classes:

            if class_name in grid_map:

                applied_width = grid_map[
                    class_name
                ]

        if applied_width:

            styles.append(
                f"flex:0 0 {applied_width};"
            )

            styles.append(
                f"max-width:{applied_width};"
            )

            styles.append(
                f"width:{applied_width};"
            )

        # =================================================
        # FLEX DIRECTION COLUMN
        # =================================================

        if (
            "oj-sm-flex-direction-column"
            in classes
        ):

            styles.append(
                "display:flex;"
            )

            styles.append(
                "flex-direction:column;"
            )

        # =================================================
        # ALIGN SELF
        # =================================================

        if (
            "oj-sm-align-self-flex-start"
            in classes
        ):

            styles.append(
                "align-self:flex-start;"
            )

        # =================================================
        # FLEX WRAP NOWRAP
        # =================================================

        if (
            "oj-sm-flex-wrap-nowrap"
            in classes
        ):

            styles.append(
                "flex-wrap:nowrap;"
            )

        # =================================================
        # JUSTIFY CONTENT
        # =================================================

        justify_map = {

            "oj-sm-justify-content-center":
                "center",

            "oj-sm-justify-content-flex-end":
                "flex-end",

            "oj-sm-justify-content-space-between":
                "space-between",

            "oj-sm-justify-content-space-around":
                "space-around"
        }

        for class_name in classes:

            if class_name in justify_map:

                styles.append(
                    f"justify-content:{justify_map[class_name]};"
                )

        # =================================================
        # ALIGN ITEMS
        # =================================================

        align_map = {

            "oj-sm-align-items-center":
                "center",

            "oj-sm-align-items-flex-start":
                "flex-start",

            "oj-sm-align-items-flex-end":
                "flex-end"
        }

        for class_name in classes:

            if class_name in align_map:

                styles.append(
                    f"align-items:{align_map[class_name]};"
                )


        # =================================================
        # APPLY STYLE
        # =================================================

        if styles:

            current_style = tag.get(
                "style",
                ""
            )

            tag["style"] = (
                current_style
                + ";"
                + " ".join(styles)
            )



# =========================================================
# FLEX ITEM
# =========================================================

def translate_oj_flex_item(
    soup
):

    tags = soup.find_all(
        class_=lambda c:
        c and "oj-flex-item" in c
    )

    for tag in tags:

        current_style = tag.get(
            "style",
            ""
        )

        classes = tag.get(
            "class",
            []
        )

        styles = [
            "box-sizing:border-box;",
            "min-width:0;"
        ]

        # =================================================
        # FLEX INITIAL
        # =================================================

        if (
            "oj-sm-flex-initial"
            in classes
        ):

            styles.extend([
                "flex-grow:0;",
                "flex-shrink:1;",
                "flex-basis:auto;",
                "width:auto;"
            ])

        else:

            styles.extend([
                "flex-grow:0;",
                "flex-shrink:1;",
                "flex-basis:auto;"
            ])

        # =================================================
        # BUTTONS SHOULD NEVER STRETCH
        # =================================================

        if tag.find("button"):

            styles.extend([
                "width:auto;",
                "height:auto;",
                "align-self:flex-start;",
                "flex-grow:0;",
                "flex-basis:auto;"
            ])

        # =================================================
        # APPLY
        # =================================================

        tag["style"] = (
            current_style
            + ";"
            + " ".join(styles)
        )


# =========================================================
# FLEX
# =========================================================

def translate_oj_flex(
    soup
):

    tags = soup.find_all(
        class_=lambda c:
        c and "oj-flex" in c
    )

    for tag in tags:

        classes = tag.get(
            "class",
            []
        )

        current_style = tag.get(
            "style",
            ""
        )

        # =================================================
        # DEFAULTS
        # =================================================

        direction = "row"
        wrap = "nowrap"
        justify = "flex-start"
        align = "stretch"

        # =================================================
        # AUTO DETECT SECTION CONTAINERS
        # =================================================

        direct_children = tag.find_all(
            recursive=False
        )

        has_title_child = False
        has_nested_flex = False

        for child in direct_children:

            child_classes = child.get(
                "class",
                []
            )

            child_id = child.get(
                "id",
                ""
            ).lower()

            joined = (
                " ".join(child_classes)
                + " "
                + child_id
            ).lower()

            # =============================================
            # TITLES
            # =============================================

            if (
                "titulo" in joined
                or
                "subtitulo" in joined
            ):

                has_title_child = True

            # =============================================
            # NESTED FLEX
            # =============================================

            if (
                "oj-flex" in child_classes
            ):

                has_nested_flex = True

        # =================================================
        # SECTION WRAPPERS
        # =================================================

        # =================================================
        # AUTO DETECT REAL VB SECTIONS
        # =================================================

        nested_flex_count = 0
        has_table = False
        has_form_layout = False
        button_count = 0

        for child in direct_children:

            if child.find("button"):

                button_count += 1

            child_classes = child.get(
                "class",
                []
            )

            if (
                "oj-flex" in child_classes
            ):

                nested_flex_count += 1

            if child.find("table"):

                has_table = True

            if child.find(
                class_="vb-form-layout"
            ):

                has_form_layout = True

        # =================================================
        # REAL SECTION WRAPPERS
        # =================================================

        if (

            has_title_child

            and

            (
                has_table
                or
                has_form_layout
                or
                nested_flex_count >= 2
            )
        ):

            direction = "column"

        # =================================================
        # TOOLBAR + TABLE SECTION
        # =================================================

        if (
            has_table
            and
            button_count >= 2
        ):

            direction = "column"

        # =================================================
        # EXPLICIT COLUMN
        # =================================================

        if (
            "oj-sm-flex-direction-column"
            in classes
        ):

            direction = "column"

        # =================================================
        # WRAP
        # =================================================

        if (
            "oj-flex-wrap" in " ".join(classes)
        ):

            wrap = "wrap"

        # =================================================
        # JUSTIFY
        # =================================================

        if (
            "oj-sm-justify-content-center"
            in classes
        ):

            justify = "center"

        elif (
            "oj-sm-justify-content-space-between"
            in classes
        ):

            justify = "space-between"

        elif (
            "oj-sm-justify-content-space-around"
            in classes
        ):

            justify = "space-around"

        elif (
            "oj-sm-justify-content-flex-end"
            in classes
        ):

            justify = "flex-end"

        # =================================================
        # ALIGN
        # =================================================

        if (
            "oj-sm-align-items-center"
            in classes
        ):

            align = "center"

        elif (
            "oj-sm-align-items-flex-start"
            in classes
        ):

            align = "flex-start"

        elif (
            "oj-sm-align-items-flex-end"
            in classes
        ):

            align = "flex-end"

        # =================================================
        # TITLE CONTAINERS
        # =================================================

        is_title = False

        ids_and_classes = (
            " ".join(classes)
            + " "
            + tag.get("id", "")
        ).lower()

        if (
            "titulo" in ids_and_classes
            or
            "subtitulo" in ids_and_classes
        ):

            is_title = True

        # =================================================
        # BASE STYLE
        # =================================================

        styles = [
            "display:flex;",
            f"flex-direction:{direction};",
            f"justify-content:{justify};",
            f"align-items:{align};",
            f"flex-wrap:{wrap};",
            "gap:24px;",
            "box-sizing:border-box;",
            "min-width:0;"
        ]

        # =================================================
        # ONLY SOME ROWS SHOULD FORCE FULL WIDTH
        # =================================================

        if (
            direction == "row"
            and
            not is_title
            and
            "oj-flex-item" not in classes
        ):

            styles.append(
                "width:100%;"
            )

        # =================================================
        # TITLE TUNING
        # =================================================

        if is_title:

            styles.extend([
                "gap:4px;",
                "align-items:flex-start;"
            ])

        # =================================================
        # APPLY
        # =================================================

        tag["style"] = (
            current_style
            + ";"
            + " ".join(styles)
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

        value = tag.get(
            "value",
            ""
        )

        if "[[" in value:

            value = ""

        span.string = value

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

# =========================================================
# REMOVE TEMPLATES
# =========================================================

def remove_templates(
    soup
):

    templates = soup.find_all(
        "template"
    )

    for template in templates:

        template.decompose()

# =========================================================
# FLATTEN BIND IF
# =========================================================

def flatten_bind_if(
    soup
):

    tags = soup.find_all(
        "oj-bind-if"
    )

    for tag in tags:

        children = list(
            tag.contents
        )

        for child in reversed(
            children
        ):
            tag.insert_after(
                child
            )

        tag.decompose()

# =========================================================
# FLATTEN BIND FOR EACH
# =========================================================

def flatten_bind_for_each(
    soup
):

    tags = soup.find_all(
        "oj-bind-for-each"
    )

    for tag in tags:

        template = tag.find(
            "template"
        )

        if template:

            children = list(
                template.contents
            )

            for child in reversed(
                children
            ):
                tag.insert_after(
                    child
                )

        tag.decompose()