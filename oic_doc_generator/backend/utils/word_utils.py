# =========================================================
# FILE:
# oic_doc_generator/utils/word_utils.py
# =========================================================

from docx.shared import (
    Pt,
    RGBColor
)

from docx.enum.text import (
    WD_PARAGRAPH_ALIGNMENT
)

from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls


# =========================================================
# CREATE HEADER
# =========================================================

def create_header(
    document,
    text,
    size=16
):

    if "." in text:

        p = document.add_paragraph(
            style="Heading 2"
        )

        p.style = "HD2"

    else:

        p = document.add_paragraph(
            style="Heading 1"
        )

        p.style = "HD1"

    run = p.add_run(text)

    run.bold = True

    run.font.name = "Arial"

    run.font.size = Pt(size)

    p.alignment = (
        WD_PARAGRAPH_ALIGNMENT.LEFT
    )
    
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

    cell = table.rows[0].cells[0]

    cell.width = Pt(450)

    shading = parse_xml(

        r'<w:shd {} w:fill="D8E4BC"/>'.format(
            nsdecls('w')
        )
    )

    cell._tc.get_or_add_tcPr().append(
        shading
    )

    p = cell.paragraphs[0]

    run = p.add_run(text)

    run.font.name = "Candara"

    run.font.size = Pt(10)

    run.font.color.rgb = RGBColor(
        0,
        0,
        0
    )

    p.alignment = (
        WD_PARAGRAPH_ALIGNMENT.LEFT
    )
