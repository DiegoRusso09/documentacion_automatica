# =========================================================
# FILE:
# oic_doc_generator/utils/code_block_utils.py
# =========================================================

from docx.shared import (
    Pt,
    RGBColor
)

from docx.enum.text import (
    WD_PARAGRAPH_ALIGNMENT
)

from docx.enum.style import WD_STYLE_TYPE

from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn


# =========================================================
# SQL KEYWORDS
# =========================================================

SQL_KEYWORDS = [

    "SELECT",
    "FROM",
    "WHERE",
    "AND",
    "OR",
    "ORDER",
    "GROUP",
    "BY",
    "INNER",
    "LEFT",
    "RIGHT",
    "JOIN",
    "ON",
    "UNION",
    "DISTINCT",
    "AS",
    "CASE",
    "WHEN",
    "THEN",
    "ELSE",
    "END",
    "EXISTS",
    "NOT",
    "NULL",
    "LIKE",
    "IN",
    "BETWEEN",
    "HAVING",
    "INSERT",
    "UPDATE",
    "DELETE",
    "CREATE",
    "ALTER",
    "DROP",
    "PACKAGE",
    "BODY",
    "PROCEDURE",
    "FUNCTION",
    "RETURN",
    "BEGIN",
    "EXCEPTION",
    "LOOP",
    "FOR",
    "WHILE",
    "IF"
]

SQL_KEYWORD_SET = set(SQL_KEYWORDS)


# =========================================================
# CREATE SHADED PARAGRAPH
# =========================================================

def create_shaded_paragraph(
    document
):

    paragraph = document.add_paragraph()

    paragraph.alignment = (
        WD_PARAGRAPH_ALIGNMENT.LEFT
    )

    shading = parse_xml(

        r'<w:shd {} w:fill="1E1E1E"/>'.format(
            nsdecls('w')
        )
    )

    paragraph._p.get_or_add_pPr().append(
        shading
    )

    return paragraph


# =========================================================
# ADD COLORED RUN
# =========================================================

def add_colored_run(
    paragraph,
    text,
    color
):

    run = paragraph.add_run(
        text
    )

    run.font.name = "Consolas"

    run.font.size = Pt(9)

    run.font.color.rgb = color

    return run


# =========================================================
# PROCESS TOKEN
# =========================================================

def process_token(
    paragraph,
    token
):

    clean = token.strip()

    upper = clean.upper()

    # =====================================================
    # KEYWORD
    # =====================================================

    if upper in SQL_KEYWORDS:

        add_colored_run(

            paragraph,

            token + " ",

            RGBColor(
                86,
                156,
                214
            )
        )

        return

    # =====================================================
    # VARIABLE
    # =====================================================

    if clean.startswith(":"):

        add_colored_run(

            paragraph,

            token + " ",

            RGBColor(
                78,
                201,
                176
            )
        )

        return

    # =====================================================
    # STRING
    # =====================================================

    if (
        clean.startswith("'")
        and
        clean.endswith("'")
    ):

        add_colored_run(

            paragraph,

            token + " ",

            RGBColor(
                214,
                157,
                133
            )
        )

        return

    # =====================================================
    # DEFAULT
    # =====================================================

    add_colored_run(

        paragraph,

        token + " ",

        RGBColor(
            220,
            220,
            220
        )
    )


# =========================================================
# FAST, LOW-MEMORY RUNS
# =========================================================
#
# Un catálogo BIP puede traer millones de caracteres de SQL.
# Para que la generación sea rápida y quepa en poca memoria
# (Render free: 512 MB):
#   - cada color es un ESTILO DE CARÁCTER de Word (Consolas
#     9 pt + color); el run solo lo referencia (w:rStyle) en
#     vez de repetir fuente, tamaño y color;
#   - el texto seguido del mismo color va en UN run, aunque
#     cruce saltos de línea (w:t y w:br dentro del mismo run);
#   - un bloque muy grande va en un solo color, sin resaltar
#     palabras clave (el texto queda completo).
# =========================================================

COLOR_KEYWORD = "569CD6"

COLOR_VARIABLE = "4EC9B0"

COLOR_STRING = "D69D85"

COLOR_DEFAULT = "DCDCDC"

COLOR_COMMENT = "6A9955"

CODE_STYLES = {
    COLOR_KEYWORD: "Codigo SQL clave",
    COLOR_VARIABLE: "Codigo SQL variable",
    COLOR_STRING: "Codigo SQL texto",
    COLOR_DEFAULT: "Codigo SQL",
    COLOR_COMMENT: "Codigo SQL comentario"
}

# Bloques más grandes: un solo color (sin resaltado).
MAX_HIGHLIGHT_CHARS = 30000

BREAK = None


def _style_id(document, color):

    # Crea (una vez por documento) el estilo de carácter del
    # color y devuelve su id.
    cache = document.__dict__.setdefault("_code_style_ids", {})

    if color in cache:
        return cache[color]

    name = CODE_STYLES[color]

    styles = document.styles

    try:

        style = styles[name]

    except KeyError:

        style = styles.add_style(name, WD_STYLE_TYPE.CHARACTER)

        style.font.name = "Consolas"

        style.font.size = Pt(9)

        style.font.color.rgb = RGBColor.from_string(color)

        style.hidden = True

    cache[color] = style.style_id

    return style.style_id


def _append_run(document, paragraph, color, pieces):

    # pieces: textos y BREAK (salto de línea), en orden.
    run = OxmlElement("w:r")

    properties = OxmlElement("w:rPr")

    style = OxmlElement("w:rStyle")

    style.set(qn("w:val"), _style_id(document, color))

    properties.append(style)

    run.append(properties)

    for piece in pieces:

        if piece is BREAK:

            run.append(OxmlElement("w:br"))

        else:

            text_element = OxmlElement("w:t")

            text_element.set(qn("xml:space"), "preserve")

            text_element.text = piece

            run.append(text_element)

    paragraph._p.append(run)


def _token_color(token):

    clean = token.strip()

    if clean.upper() in SQL_KEYWORD_SET:
        return COLOR_KEYWORD

    if clean.startswith(":"):
        return COLOR_VARIABLE

    if clean.startswith("'") and clean.endswith("'"):
        return COLOR_STRING

    return COLOR_DEFAULT


def _segments(text):

    # [(color, texto)] con BREAK entre líneas, en orden.
    lines = text.split("\n")

    highlight = len(text) <= MAX_HIGHLIGHT_CHARS

    for idx, line in enumerate(lines):

        if not highlight:

            yield COLOR_DEFAULT, line

        elif line.strip().startswith("--"):

            yield COLOR_COMMENT, line

        else:

            for token in line.split(" "):
                yield _token_color(token), token + " "

        if idx < len(lines) - 1:
            yield None, BREAK


# =========================================================
# ADD CODE BLOCK
# =========================================================

def add_code_block(
    document,
    text,
    language=None
):

    if not text:

        return

    paragraph = create_shaded_paragraph(
        document
    )

    current_color = None

    pieces = []

    for color, piece in _segments(text):

        # El salto de línea va con el run en curso.
        if piece is BREAK:
            pieces.append(BREAK)
            continue

        if color != current_color and pieces:
            _append_run(document, paragraph, current_color, pieces)
            pieces = []

        current_color = color

        # Textos seguidos del mismo color: un solo w:t.
        if pieces and pieces[-1] is not BREAK:
            pieces[-1] += piece
        else:
            pieces.append(piece)

    if pieces:

        if current_color is None:
            current_color = COLOR_DEFAULT

        _append_run(document, paragraph, current_color, pieces)
