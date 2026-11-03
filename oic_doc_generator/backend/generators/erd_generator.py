# =========================================================
# FILE: erd_generator.py
# =========================================================
#
# Diagrama entidad-relación (sección 7.1 del DS140).
#
#   - Tablas padre arriba, hijas abajo (niveles según las FK),
#     ordenadas para que las líneas se crucen lo menos posible.
#   - Cada tabla muestra sus columnas PK y FK con su tipo, y
#     cuántas columnas más tiene.
#   - Relaciones en notación IE ("pata de gallo"): lado muchos
#     en la tabla hija, lado uno en la padre. Las líneas van
#     por los pasillos entre cajas, nunca por encima del texto.
#   - Tablas sin relaciones: al final.
#
# Medidas en pulgadas, para el ancho útil del Word (5.7"),
# igual que los demás diagramas (matplotlib).
# =========================================================

import os
import tempfile

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from matplotlib.patches import FancyBboxPatch


PAGE_WIDTH = 5.7

DPI = 220

COLUMNS = 3

MARGIN = 0.05

GAP_X = 0.3

GAP_Y = 0.42

HEADER_HEIGHT = 0.22

ROW_HEIGHT = 0.13

PADDING = 0.05

TITLE_SPACE = 0.34

FONT_TITLE = 10

FONT_TABLE = 7

FONT_ROW = 6

HEADER_COLOR = "#4F9BE0"

BODY_COLOR = "#FFFFFF"

EDGE_COLOR = "#333333"

LINE_COLOR = "#5A6B7B"

MUTED_COLOR = "#777777"

BOLD_CHAR_WIDTH = 0.7 / 72

CHAR_WIDTH = 0.62 / 72


# =========================================================
# MODEL
# =========================================================

def _name(table):

    return (table.get("table_name") or "TABLA").upper()


def _relations(tables):

    names = {_name(table) for table in tables}

    relations = []

    for table in tables:

        child = _name(table)

        for foreign_key in table.get("foreign_keys", []):

            parent = (foreign_key.get("referenced_table") or "").upper()

            parent = parent.replace('"', "").split(".")[-1]

            if parent in names and parent != child:

                relations.append({
                    "child": child,
                    "parent": parent,
                    "column": (foreign_key.get("column") or "").upper()
                })

    return relations


def _levels(tables, relations):

    parents = {}

    for relation in relations:
        parents.setdefault(relation["child"], set()).add(relation["parent"])

    levels = {}

    def level_of(name, visiting=()):

        if name in levels:
            return levels[name]

        if name in visiting:
            return 0

        level = 0

        for parent in parents.get(name, ()):
            level = max(level, level_of(parent, visiting + (name,)) + 1)

        levels[name] = level

        return level

    for table in tables:
        level_of(_name(table))

    return levels


def _rows(table):

    # Columnas a mostrar: PK y FK con su tipo.
    pk = {column.upper() for column in table.get("primary_keys", [])}

    fk = {
        (foreign_key.get("column") or "").upper()
        for foreign_key in table.get("foreign_keys", [])
    }

    rows = []

    columns = table.get("columns", [])

    for column in columns:

        name = (column.get("column_name") or "").upper()

        tags = [tag for tag, keys in (("PK", pk), ("FK", fk)) if name in keys]

        if tags:
            rows.append((",".join(tags), name, column.get("data_type", "")))

    hidden = len(columns) - len(rows)

    if not rows:
        rows.append(("", "(sin PK ni FK)", ""))

    if hidden > 0:
        rows.append(("", f"+ {hidden} {'columna' if hidden == 1 else 'columnas'}", ""))

    return rows


def _box_height(rows):

    return HEADER_HEIGHT + PADDING * 2 + len(rows) * ROW_HEIGHT


# =========================================================
# LAYOUT
# =========================================================

def _layout(tables, relations, levels, box_width):

    by_name = {_name(table): table for table in tables}

    linked = {relation["child"] for relation in relations} | {
        relation["parent"] for relation in relations
    }

    groups = {}

    for name in by_name:

        level = levels.get(name, 0) if name in linked else None

        groups.setdefault(level, []).append(name)

    ordered_levels = sorted(key for key in groups if key is not None)

    if None in groups:
        ordered_levels.append(None)

    positions = {}

    rows = []

    y = 0.0

    parents_of = {}

    for relation in relations:
        parents_of.setdefault(relation["child"], []).append(relation["parent"])

    for level in ordered_levels:

        names = groups[level]

        # Orden por la posición de sus padres (menos cruces).
        def barycenter(name):

            xs = [
                positions[parent][0]
                for parent in parents_of.get(name, [])
                if parent in positions
            ]

            return (sum(xs) / len(xs)) if xs else 0

        names.sort(key=lambda name: (barycenter(name), name))

        for start in range(0, len(names), COLUMNS):

            chunk = names[start:start + COLUMNS]

            row_width = len(chunk) * box_width + (len(chunk) - 1) * GAP_X

            x = (PAGE_WIDTH - row_width) / 2

            height = max(_box_height(_rows(by_name[name])) for name in chunk)

            for name in chunk:

                positions[name] = (x, y, _box_height(_rows(by_name[name])))

                x += box_width + GAP_X

            rows.append((y, height))

            y += height + GAP_Y

    return positions, rows, y - GAP_Y


# =========================================================
# DRAW
# =========================================================

def _fit(text, width, font_size, minimum, char_width):

    needed = len(text) * font_size * char_width

    if needed <= width:
        return font_size

    return max(minimum, font_size * width / needed)


def _draw_table(ax, x, top, width, name, rows):

    height = _box_height(rows)

    ax.add_patch(
        FancyBboxPatch(
            (x, top - height),
            width,
            height,
            boxstyle="round,pad=0,rounding_size=0.03",
            linewidth=1,
            edgecolor=EDGE_COLOR,
            facecolor=BODY_COLOR,
            zorder=3
        )
    )

    ax.add_patch(
        FancyBboxPatch(
            (x, top - HEADER_HEIGHT),
            width,
            HEADER_HEIGHT,
            boxstyle="round,pad=0,rounding_size=0.03",
            linewidth=1,
            edgecolor=EDGE_COLOR,
            facecolor=HEADER_COLOR,
            zorder=4
        )
    )

    ax.text(
        x + width / 2,
        top - HEADER_HEIGHT / 2,
        name,
        ha="center",
        va="center",
        fontsize=_fit(name, width - 0.08, FONT_TABLE, 4.8, BOLD_CHAR_WIDTH),
        fontweight="bold",
        color="white",
        zorder=5
    )

    y = top - HEADER_HEIGHT - PADDING - ROW_HEIGHT / 2

    for tag, column, data_type in rows:

        muted = not tag

        if tag:

            ax.text(
                x + 0.05,
                y,
                tag,
                ha="left",
                va="center",
                fontsize=FONT_ROW - 0.6,
                fontweight="bold",
                color="#B5651D" if "PK" in tag else "#2E7D32",
                zorder=5
            )

        name_x = x + (0.36 if tag or not muted else 0.05)

        type_width = len(data_type) * (FONT_ROW - 0.8) * CHAR_WIDTH

        ax.text(
            name_x,
            y,
            column,
            ha="left",
            va="center",
            fontsize=_fit(
                column,
                width - (name_x - x) - type_width - 0.1,
                FONT_ROW,
                4.5,
                CHAR_WIDTH
            ),
            fontstyle="italic" if muted else "normal",
            color=MUTED_COLOR if muted else "#222222",
            zorder=5
        )

        if data_type:

            ax.text(
                x + width - 0.05,
                y,
                data_type,
                ha="right",
                va="center",
                fontsize=FONT_ROW - 0.8,
                color=MUTED_COLOR,
                zorder=5
            )

        y -= ROW_HEIGHT

    return height


def _crow_foot(ax, x, y, direction):

    # Lado "muchos": tres trazos que abren hacia la tabla hija.
    tip = y + 0.08 * direction

    for dx in (-0.045, 0, 0.045):
        ax.plot([x, x + dx], [tip, y], color=LINE_COLOR, linewidth=0.9, zorder=2)


def _one_bar(ax, x, y, direction):

    # Lado "uno": barra perpendicular junto a la tabla padre.
    bar_y = y - 0.05 * direction

    ax.plot([x - 0.045, x + 0.045], [bar_y, bar_y], color=LINE_COLOR, linewidth=0.9, zorder=2)


def generate_erd_diagram(
    tables
):

    if not tables:
        return None

    relations = _relations(tables)

    levels = _levels(tables, relations)

    box_width = (PAGE_WIDTH - 2 * MARGIN - (COLUMNS - 1) * GAP_X) / COLUMNS

    positions, rows, content_height = _layout(tables, relations, levels, box_width)

    total_height = TITLE_SPACE + content_height + 0.15

    figure = plt.figure(figsize=(PAGE_WIDTH, total_height), dpi=DPI)

    ax = figure.add_axes([0, 0, 1, 1])

    ax.set_xlim(0, PAGE_WIDTH)

    ax.set_ylim(0, total_height)

    ax.axis("off")

    ax.text(
        PAGE_WIDTH / 2,
        total_height - TITLE_SPACE / 2,
        "Modelo Entidad Relación",
        ha="center",
        va="center",
        fontsize=FONT_TITLE,
        fontweight="bold",
        color="#111111"
    )

    origin = total_height - TITLE_SPACE

    by_name = {_name(table): table for table in tables}

    boxes = {}

    for name, (x, offset, _height) in positions.items():

        top = origin - offset

        height = _draw_table(ax, x, top, box_width, name, _rows(by_name[name]))

        boxes[name] = (x, top, height)

    # Pasillos verticales entre columnas (x libres de cajas).
    gutters = [MARGIN / 2] + [
        MARGIN + box_width * (index + 1) + GAP_X * index + GAP_X / 2
        for index in range(COLUMNS - 1)
    ] + [PAGE_WIDTH - MARGIN / 2]

    # Varias líneas que salen de una misma caja se separan.
    used = {}

    offsets = (0, -0.2, 0.2, -0.35, 0.35)

    def slot(name, side):

        # Centro, luego a los lados: 1.ª línea al medio, etc.
        key = (name, side)

        count = used.get(key, 0)

        used[key] = count + 1

        x, _top, _height = boxes[name]

        return x + box_width * (0.5 + offsets[count % len(offsets)])

    for index, relation in enumerate(relations):

        child_x0, child_top, _child_height = boxes[relation["child"]]

        parent_x0, parent_top, parent_height = boxes[relation["parent"]]

        parent_bottom = parent_top - parent_height

        cx = min(max(slot(relation["child"], "top"), child_x0 + 0.1), child_x0 + box_width - 0.1)

        px = min(max(slot(relation["parent"], "bottom"), parent_x0 + 0.1), parent_x0 + box_width - 0.1)

        lane = (index % 4) * 0.035

        if child_top < parent_bottom:

            # Padre más arriba: sube por el pasillo.
            y_child = child_top + GAP_Y * 0.3 + lane

            y_parent = parent_bottom - GAP_Y * 0.3 - lane

            adjacent = y_child >= y_parent - 0.01

            if adjacent:

                y_mid = (child_top + parent_bottom) / 2 + lane - 0.05

                points = [(cx, child_top), (cx, y_mid), (px, y_mid), (px, parent_bottom)]

            else:

                gutter = min(gutters, key=lambda gx: abs(gx - (cx + px) / 2))

                points = [
                    (cx, child_top), (cx, y_child), (gutter, y_child),
                    (gutter, y_parent), (px, y_parent), (px, parent_bottom)
                ]

            ax.plot(
                [point[0] for point in points],
                [point[1] for point in points],
                color=LINE_COLOR,
                linewidth=0.9,
                zorder=2
            )

            _crow_foot(ax, cx, child_top, 1)

            _one_bar(ax, px, parent_bottom, 1)

        else:

            # Mismo nivel (ciclo de FK): línea por el pasillo.
            gutter = min(gutters, key=lambda gx: abs(gx - (cx + px) / 2))

            y_line = min(child_top, parent_top) + GAP_Y * 0.3 + lane

            points = [(cx, child_top), (cx, y_line), (px, y_line), (px, parent_top)]

            ax.plot(
                [point[0] for point in points],
                [point[1] for point in points],
                color=LINE_COLOR,
                linewidth=0.9,
                linestyle=(0, (3, 2)),
                zorder=2
            )

    # Leyenda de la notación.
    ax.text(
        PAGE_WIDTH - MARGIN,
        0.07,
        "Notación: ─┼ uno   ─< muchos",
        ha="right",
        va="center",
        fontsize=5.5,
        color=MUTED_COLOR
    )

    png_file = os.path.join(tempfile.mkdtemp(), "erd.png")

    figure.savefig(png_file, dpi=DPI, facecolor="white")

    plt.close(figure)

    return png_file
