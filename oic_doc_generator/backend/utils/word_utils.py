# =========================================================
# FILE:
# oic_doc_generator/backend/utils/word_utils.py
# =========================================================

import re


from docx.shared import (
    Pt,
    RGBColor,
    Cm
)

from docx.enum.text import (
    WD_PARAGRAPH_ALIGNMENT
)

from docx.oxml import (
    parse_xml,
    OxmlElement
)

from docx.oxml.ns import (
    nsdecls,
    qn
)


# =========================================================
# HEADER NUMBER REGEX
# =========================================================
#
# Ejemplos reconocidos:
#
# 1\tControl del Documento
# 1.1\tRegistro de Modificaciones
# 2\tVisión General
# 2.1\tReglas del Negocio
# 10.2\tTemas Cerrados
#
# =========================================================

HEADER_NUMBER_PATTERN = re.compile(

    r"^\s*"
    r"(\d+(?:\.\d+)*)"
    r"\t+"
    r"(.*)$"

)


# =========================================================
# GET NEXT NUMERIC ID
# =========================================================

def _get_next_numeric_id(
    elements,
    attribute_name
):

    values = []


    for element in elements:

        value = element.get(
            qn(
                attribute_name
            )
        )


        if value is None:

            continue


        try:

            values.append(
                int(
                    value
                )
            )

        except Exception:

            continue


    if not values:

        return 0


    return (
        max(
            values
        )
        + 1
    )


# =========================================================
# CREATE MULTILEVEL NUMBERING DEFINITION
# =========================================================

def _create_heading_abstract_numbering(
    document
):

    numbering = (
        document
        .part
        .numbering_part
        .element
    )


    abstract_num_id = (
        _get_next_numeric_id(

            numbering.findall(
                qn(
                    "w:abstractNum"
                )
            ),

            "w:abstractNumId"
        )
    )


    # =====================================================
    # ABSTRACT NUMBER
    # =====================================================

    abstract_num = OxmlElement(
        "w:abstractNum"
    )


    abstract_num.set(

        qn(
            "w:abstractNumId"
        ),

        str(
            abstract_num_id
        )
    )


    # =====================================================
    # MULTILEVEL
    # =====================================================

    multi_level_type = OxmlElement(
        "w:multiLevelType"
    )


    multi_level_type.set(

        qn(
            "w:val"
        ),

        "multilevel"
    )


    abstract_num.append(
        multi_level_type
    )


    # =====================================================
    # CREATE LEVELS
    # =====================================================
    #
    # Nivel 0:
    #   1
    #
    # Nivel 1:
    #   1.1
    #
    # Nivel 2:
    #   1.1.1
    #
    # etc.
    #
    # =====================================================

    for level in range(
        9
    ):

        lvl = OxmlElement(
            "w:lvl"
        )


        lvl.set(

            qn(
                "w:ilvl"
            ),

            str(
                level
            )
        )


        # ================================================
        # START
        # ================================================

        start = OxmlElement(
            "w:start"
        )


        start.set(

            qn(
                "w:val"
            ),

            "1"
        )


        lvl.append(
            start
        )


        # ================================================
        # NUMBER FORMAT
        # ================================================

        num_format = OxmlElement(
            "w:numFmt"
        )


        num_format.set(

            qn(
                "w:val"
            ),

            "decimal"
        )


        lvl.append(
            num_format
        )


        # ================================================
        # NUMBER FORMAT TEXT
        # ================================================
        #
        # 0 -> %1
        # 1 -> %1.%2
        # 2 -> %1.%2.%3
        #
        # ================================================

        level_text_value = ".".join(

            f"%{index}"

            for index in range(
                1,
                level + 2
            )
        )


        level_text = OxmlElement(
            "w:lvlText"
        )


        level_text.set(

            qn(
                "w:val"
            ),

            level_text_value
        )


        lvl.append(
            level_text
        )


        # ================================================
        # TAB AFTER NUMBER
        # ================================================

        suffix = OxmlElement(
            "w:suff"
        )


        suffix.set(

            qn(
                "w:val"
            ),

            "tab"
        )


        lvl.append(
            suffix
        )


        # ================================================
        # ALIGN NUMBER LEFT
        # ================================================

        level_justification = OxmlElement(
            "w:lvlJc"
        )


        level_justification.set(

            qn(
                "w:val"
            ),

            "left"
        )


        lvl.append(
            level_justification
        )


        # ================================================
        # PARAGRAPH POSITION
        # ================================================
        #
        # 720 twips = 0.5 pulgadas.
        #
        # Esto reproduce aproximadamente la tabulación que
        # actualmente existe entre:
        #
        # 2     Visión General
        #
        # ================================================

        paragraph_properties = OxmlElement(
            "w:pPr"
        )


        tabs = OxmlElement(
            "w:tabs"
        )


        tab = OxmlElement(
            "w:tab"
        )


        tab.set(

            qn(
                "w:val"
            ),

            "num"
        )


        tab.set(

            qn(
                "w:pos"
            ),

            "720"
        )


        tabs.append(
            tab
        )


        paragraph_properties.append(
            tabs
        )


        indent = OxmlElement(
            "w:ind"
        )


        indent.set(

            qn(
                "w:left"
            ),

            "720"
        )


        indent.set(

            qn(
                "w:hanging"
            ),

            "720"
        )


        paragraph_properties.append(
            indent
        )


        lvl.append(
            paragraph_properties
        )


        abstract_num.append(
            lvl
        )


    numbering.append(
        abstract_num
    )


    return abstract_num_id


# =========================================================
# CREATE NUMBERING INSTANCE
# =========================================================

def _create_heading_numbering_instance(
    document,
    abstract_num_id,
    start_at=1
):

    numbering = (
        document
        .part
        .numbering_part
        .element
    )


    num_id = (
        _get_next_numeric_id(

            numbering.findall(
                qn(
                    "w:num"
                )
            ),

            "w:numId"
        )
    )


    # =====================================================
    # NUM
    # =====================================================

    num = OxmlElement(
        "w:num"
    )


    num.set(

        qn(
            "w:numId"
        ),

        str(
            num_id
        )
    )


    # =====================================================
    # ABSTRACT REFERENCE
    # =====================================================

    abstract_reference = OxmlElement(
        "w:abstractNumId"
    )


    abstract_reference.set(

        qn(
            "w:val"
        ),

        str(
            abstract_num_id
        )
    )


    num.append(
        abstract_reference
    )


    # =====================================================
    # OPTIONAL START OVERRIDE
    # =====================================================
    #
    # Esto permite conservar casos como:
    #
    # 8 Control de Accesos
    # 10 Temas Abiertos y Cerrados
    #
    # Si deliberadamente no existe una sección 9,
    # Word no cambiará el 10 por un 9.
    #
    # =====================================================

    if start_at != 1:

        level_override = OxmlElement(
            "w:lvlOverride"
        )


        level_override.set(

            qn(
                "w:ilvl"
            ),

            "0"
        )


        start_override = OxmlElement(
            "w:startOverride"
        )


        start_override.set(

            qn(
                "w:val"
            ),

            str(
                start_at
            )
        )


        level_override.append(
            start_override
        )


        num.append(
            level_override
        )


    numbering.append(
        num
    )


    return num_id


# =========================================================
# GET DS140 NUMBERING STATE
# =========================================================

def _get_heading_numbering_state(
    document
):

    state = getattr(

        document,

        "_ds140_heading_numbering",

        None
    )


    if state is not None:

        return state


    abstract_num_id = (
        _create_heading_abstract_numbering(
            document
        )
    )


    num_id = (
        _create_heading_numbering_instance(

            document,

            abstract_num_id,

            start_at=1
        )
    )


    state = {

        "abstract_num_id":
            abstract_num_id,

        "num_id":
            num_id,

        "last_top_level":
            0
    }


    setattr(

        document,

        "_ds140_heading_numbering",

        state
    )


    return state


# =========================================================
# APPLY NUMBERING TO PARAGRAPH
# =========================================================

def _apply_heading_numbering(
    paragraph,
    num_id,
    level,
    size
):

    paragraph_properties = (
        paragraph
        ._p
        .get_or_add_pPr()
    )


    # =====================================================
    # NUMBER PROPERTIES
    # =====================================================

    num_properties = (
        paragraph_properties
        .get_or_add_numPr()
    )


    level_element = (
        num_properties
        .get_or_add_ilvl()
    )


    level_element.val = (
        level - 1
    )


    num_id_element = (
        num_properties
        .get_or_add_numId()
    )


    num_id_element.val = (
        num_id
    )


    # =====================================================
    # PARAGRAPH MARK FORMAT
    # =====================================================
    #
    # La numeración automática de Word utiliza el formato
    # del paragraph mark.
    #
    # Esto hace que el número tenga el mismo Arial,
    # negrita y tamaño que el título.
    #
    # =====================================================

    paragraph_run_properties = (
        paragraph_properties.find(
            qn(
                "w:rPr"
            )
        )
    )


    if paragraph_run_properties is None:

        paragraph_run_properties = (
            OxmlElement(
                "w:rPr"
            )
        )


        paragraph_properties.append(
            paragraph_run_properties
        )


    fonts = OxmlElement(
        "w:rFonts"
    )


    fonts.set(

        qn(
            "w:ascii"
        ),

        "Arial"
    )


    fonts.set(

        qn(
            "w:hAnsi"
        ),

        "Arial"
    )


    fonts.set(

        qn(
            "w:eastAsia"
        ),

        "Arial"
    )


    paragraph_run_properties.append(
        fonts
    )


    bold = OxmlElement(
        "w:b"
    )


    paragraph_run_properties.append(
        bold
    )


    font_size = OxmlElement(
        "w:sz"
    )


    font_size.set(

        qn(
            "w:val"
        ),

        str(
            int(
                size * 2
            )
        )
    )


    paragraph_run_properties.append(
        font_size
    )


    font_size_complex = OxmlElement(
        "w:szCs"
    )


    font_size_complex.set(

        qn(
            "w:val"
        ),

        str(
            int(
                size * 2
            )
        )
    )


    paragraph_run_properties.append(
        font_size_complex
    )


# =========================================================
# GET TABLE OF CONTENTS STATE
# =========================================================

def _get_toc_state(
    document
):

    state = getattr(
        document,
        "_ds140_toc_state",
        None
    )


    if state is not None:

        return state


    state = {

        "entries": [],

        "bookmark_counter": 1
    }


    setattr(
        document,
        "_ds140_toc_state",
        state
    )


    return state


# =========================================================
# REGISTER HEADING FOR TABLE OF CONTENTS
# =========================================================

def _register_toc_heading(
    document,
    paragraph,
    run,
    number_text,
    title,
    level
):

    state = _get_toc_state(
        document
    )


    bookmark_id = (
        state[
            "bookmark_counter"
        ]
    )


    state[
        "bookmark_counter"
    ] += 1


    bookmark_name = (
        f"ds140_heading_{bookmark_id}"
    )


    # =====================================================
    # BOOKMARK START
    # =====================================================

    bookmark_start = OxmlElement(
        "w:bookmarkStart"
    )


    bookmark_start.set(
        qn("w:id"),
        str(
            bookmark_id
        )
    )


    bookmark_start.set(
        qn("w:name"),
        bookmark_name
    )


    # =====================================================
    # BOOKMARK END
    # =====================================================

    bookmark_end = OxmlElement(
        "w:bookmarkEnd"
    )


    bookmark_end.set(
        qn("w:id"),
        str(
            bookmark_id
        )
    )


    # =====================================================
    # PLACE BOOKMARK AROUND TITLE
    # =====================================================

    run._r.addprevious(
        bookmark_start
    )


    run._r.addnext(
        bookmark_end
    )


    # =====================================================
    # REGISTER ENTRY
    # =====================================================

    state[
        "entries"
    ].append({

        "number":
            number_text,

        "title":
            title,

        "text":
            f"{number_text} {title}",

        "level":
            level,

        "bookmark":
            bookmark_name
    })


# =========================================================
# CREATE INTERNAL HYPERLINK
# =========================================================

def _add_internal_hyperlink(
    paragraph,
    text,
    bookmark_name,
    bold=False
):

    hyperlink = OxmlElement(
        "w:hyperlink"
    )


    hyperlink.set(
        qn("w:anchor"),
        bookmark_name
    )


    hyperlink.set(
        qn("w:history"),
        "1"
    )


    # =====================================================
    # RUN
    # =====================================================

    run = OxmlElement(
        "w:r"
    )


    run_properties = OxmlElement(
        "w:rPr"
    )


    # =====================================================
    # FONT
    # =====================================================

    fonts = OxmlElement(
        "w:rFonts"
    )


    fonts.set(
        qn("w:ascii"),
        "Arial"
    )


    fonts.set(
        qn("w:hAnsi"),
        "Arial"
    )


    fonts.set(
        qn("w:eastAsia"),
        "Arial"
    )


    run_properties.append(
        fonts
    )


    # =====================================================
    # FONT SIZE 10 PT
    # =====================================================

    font_size = OxmlElement(
        "w:sz"
    )


    font_size.set(
        qn("w:val"),
        "20"
    )


    run_properties.append(
        font_size
    )


    font_size_complex = OxmlElement(
        "w:szCs"
    )


    font_size_complex.set(
        qn("w:val"),
        "20"
    )


    run_properties.append(
        font_size_complex
    )


    # =====================================================
    # BLACK COLOR
    # =====================================================

    color = OxmlElement(
        "w:color"
    )


    color.set(
        qn("w:val"),
        "000000"
    )


    run_properties.append(
        color
    )


    # =====================================================
    # NO UNDERLINE
    # =====================================================

    underline = OxmlElement(
        "w:u"
    )


    underline.set(
        qn("w:val"),
        "none"
    )


    run_properties.append(
        underline
    )


    # =====================================================
    # BOLD TOP LEVEL
    # =====================================================

    if bold:

        bold_element = OxmlElement(
            "w:b"
        )


        run_properties.append(
            bold_element
        )


    run.append(
        run_properties
    )


    # =====================================================
    # TEXT
    # =====================================================

    text_element = OxmlElement(
        "w:t"
    )


    text_element.text = (
        text
    )


    run.append(
        text_element
    )


    hyperlink.append(
        run
    )


    paragraph._p.append(
        hyperlink
    )


# =========================================================
# CREATE TABLE OF CONTENTS PLACEHOLDER
# =========================================================

def create_toc_table(
    document
):

    table = document.add_table(
        rows=1,
        cols=1
    )


    table.autofit = True


    # =====================================================
    # REMOVE TABLE BORDERS
    # =====================================================

    table_properties = (
        table
        ._tbl
        .tblPr
    )


    borders = OxmlElement(
        "w:tblBorders"
    )


    for border_name in [

        "top",
        "left",
        "bottom",
        "right",
        "insideH",
        "insideV"

    ]:

        border = OxmlElement(
            f"w:{border_name}"
        )


        border.set(
            qn("w:val"),
            "nil"
        )


        borders.append(
            border
        )


    table_properties.append(
        borders
    )


    return table


# =========================================================
# POPULATE TABLE OF CONTENTS
# =========================================================

def populate_toc_table(
    document,
    table
):

    state = _get_toc_state(
        document
    )


    entries = state.get(
        "entries",
        []
    )


    # =====================================================
    # FIRST DEFAULT ROW
    # =====================================================

    first_cell = (
        table
        .rows[0]
        .cells[0]
    )


    first_paragraph = (
        first_cell
        .paragraphs[0]
    )


    if not entries:

        run = first_paragraph.add_run(
            "No se encontraron secciones."
        )

        run.font.name = (
            "Arial"
        )

        run.font.size = Pt(
            10
        )

        return


    # =====================================================
    # CREATE ENTRIES
    # =====================================================

    for index, entry in enumerate(
        entries
    ):

        if index == 0:

            paragraph = (
                first_paragraph
            )

        else:

            row = (
                table
                .add_row()
            )


            paragraph = (
                row
                .cells[0]
                .paragraphs[0]
            )


        level = entry.get(
            "level",
            1
        )


        # =================================================
        # INDENT ACCORDING TO LEVEL
        # =================================================

        paragraph.paragraph_format.left_indent = Cm(
            (
                level - 1
            )
            *
            0.75
        )


        paragraph.paragraph_format.space_before = Pt(
            0
        )


        paragraph.paragraph_format.space_after = Pt(
            3
        )


        paragraph.paragraph_format.keep_together = (
            True
        )


        # =================================================
        # CLICKABLE ENTRY
        # =================================================

        _add_internal_hyperlink(

            paragraph,

            entry[
                "text"
            ],

            entry[
                "bookmark"
            ],

            bold=(
                level == 1
            )
        )


# =========================================================
# CREATE HEADER
# =========================================================

def create_header(
    document,
    text,
    size=16
):

    # =====================================================
    # DETECT REAL NUMBER
    # =====================================================

    match = HEADER_NUMBER_PATTERN.match(
        text
    )


    # =====================================================
    # NUMBERED HEADER
    # =====================================================

    if match:

        number_text = (
            match
            .group(
                1
            )
        )


        title = (
            match
            .group(
                2
            )
        )


        numbers = [

            int(
                value
            )

            for value in number_text.split(
                "."
            )
        ]


        level = len(
            numbers
        )


        # =================================================
        # STYLE
        # =================================================

        if level == 1:

            p = document.add_paragraph(
                style="Heading 1"
            )


            p.style = (
                "HD1"
            )

        else:

            p = document.add_paragraph(
                style="Heading 2"
            )


            p.style = (
                "HD2"
            )


        # =================================================
        # NUMBERING STATE
        # =================================================

        state = (
            _get_heading_numbering_state(
                document
            )
        )


        # =================================================
        # TOP LEVEL
        # =================================================
        #
        # Normalmente Word seguirá:
        #
        # 1
        # 2
        # 3
        # ...
        #
        # Pero si detectamos un salto deliberado:
        #
        # 8
        # 10
        #
        # se crea una nueva instancia que comienza en 10.
        #
        # =================================================

        if level == 1:

            explicit_number = (
                numbers[
                    0
                ]
            )


            if (
                state[
                    "last_top_level"
                ]
                ==
                0
            ):

                expected_number = 1

            else:

                expected_number = (

                    state[
                        "last_top_level"
                    ]
                    + 1
                )


            if (
                explicit_number
                !=
                expected_number
            ):

                state[
                    "num_id"
                ] = (
                    _create_heading_numbering_instance(

                        document,

                        state[
                            "abstract_num_id"
                        ],

                        start_at=
                            explicit_number
                    )
                )


            state[
                "last_top_level"
            ] = (
                explicit_number
            )


        # =================================================
        # APPLY REAL NUMBERING
        # =================================================

        _apply_heading_numbering(

            p,

            state[
                "num_id"
            ],

            level,

            size
        )


        # =================================================
        # ADD TITLE ONLY
        # =================================================
        #
        # IMPORTANTE:
        #
        # Ya NO agregamos:
        #
        # 2.1\tReglas del Negocio
        #
        # Solo agregamos:
        #
        # Reglas del Negocio
        #
        # El 2.1 será generado por Word.
        #
        # =================================================

        run = p.add_run(
            title
        )

        # =================================================
        # REGISTER IN TABLE OF CONTENTS
        # =================================================

        _register_toc_heading(

            document,

            p,

            run,

            number_text,

            title,

            level
        )


    # =====================================================
    # NON NUMBERED HEADER
    # =====================================================

    else:

        if "." in text:

            p = document.add_paragraph(
                style="Heading 2"
            )


            p.style = (
                "HD2"
            )

        else:

            p = document.add_paragraph(
                style="Heading 1"
            )


            p.style = (
                "HD1"
            )


        run = p.add_run(
            text
        )


    # =====================================================
    # CURRENT HEADER FORMAT
    # =====================================================

    run.bold = True

    run.font.name = (
        "Arial"
    )

    run.font.size = Pt(
        size
    )


    p.alignment = (
        WD_PARAGRAPH_ALIGNMENT.LEFT
    )


    return p


# =========================================================
# ADD DESCRIPTION BOX
# =========================================================

def add_description_box(
    document,
    text
):

    table = document.add_table(
        rows=1,
        cols=1
    )


    table.autofit = False


    cell = (
        table
        .rows[
            0
        ]
        .cells[
            0
        ]
    )


    cell.width = Pt(
        450
    )


    shading = parse_xml(

        r'<w:shd {} w:fill="D8E4BC"/>'.format(
            nsdecls(
                'w'
            )
        )
    )


    cell._tc.get_or_add_tcPr().append(
        shading
    )


    p = cell.paragraphs[
        0
    ]


    run = p.add_run(
        text
    )


    run.font.name = (
        "Candara"
    )


    run.font.size = Pt(
        10
    )


    run.font.color.rgb = RGBColor(
        0,
        0,
        0
    )


    p.alignment = (
        WD_PARAGRAPH_ALIGNMENT.LEFT
    )