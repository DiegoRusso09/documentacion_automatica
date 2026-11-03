# =========================================================
# FILE: sequence_diagram_generator.py
# =========================================================
#
# Diagramas de secuencia del DS140, con el mismo estilo que
# el diagrama de componentes:
#
#   - General (sección 2.4): nace del diagrama de componentes.
#     Mismos participantes (Scheduler, Clientes REST, OIC,
#     ERP, Base de datos...) y las mismas etiquetas.
#
#   - Por integración (sección 2.5): sale del árbol del flujo
#     (orchestration_parser.analyze_flow). Un participante por
#     conexión real; For/While como "loop", Switch como "alt"
#     y el manejo de errores como "error".
#
# DISEÑADO PARA LA PÁGINA DEL WORD: todo se mide en pulgadas
# y la imagen se inserta casi a tamaño real (ancho útil 5.7"),
# así la letra impresa no baja de ~7 pt. Para que eso se
# cumpla con integraciones grandes:
#   - más de MAX_PARTICIPANTS conexiones: una línea de vida
#     por SISTEMA (ERP, BD...) y la conexión va en la etiqueta;
#   - más alto que una página: se parte en "parte 1 de N",
#     cortando entre bloques principales;
#   - un bloque de error que solo notifica se resume en una
#     nota de una línea.
#
# Retornos (UML / Ambler): solo cuando el resultado se usa
# después (lo recorre un For) o es la respuesta al cliente.
#
# Se dibuja con matplotlib (sin dependencias del sistema).
# =========================================================

import os
import re
import tempfile

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from matplotlib.patches import (
    FancyArrowPatch,
    FancyBboxPatch,
    Rectangle
)

from oic_doc_generator.backend.generators.component_diagram_generator import (
    CATEGORY_BY_KEY,
    EDGE_DARK,
    OIC_COLOR,
    SOURCE_COLOR,
    _common_prefix_words,
    _strip_prefix,
    classify_connection
)

from oic_doc_generator.backend.parsers.endpoint_parser import (
    endpoint_details
)


INTEGRATION_CALL_COLOR = "#7E57C2"

MAIL_COLOR = "#8D6E63"

FRAME_COLOR = "#6B6B6B"

LIFELINE_COLOR = "#9A9A9A"

NOTE_COLOR = "#FFF4D6"

# Participantes máximos antes de agrupar por sistema.
MAX_PARTICIPANTS = 6


# =========================================================
# PAGE (pulgadas)
# =========================================================

PAGE_WIDTH = 5.7

# Alto máximo de una imagen (página carta con márgenes, menos
# el texto que la acompaña).
PAGE_HEIGHT = 7.2

DPI = 220

TITLE_HEIGHT = 0.36

HEAD_HEIGHT = 0.5

HEAD_GAP = 0.16

BOTTOM_GAP = 0.12

MSG_HEIGHT = 0.3

NOTE_HEIGHT = 0.3

FRAME_TOP = 0.25

FRAME_BOTTOM = 0.08

SECTION_GAP = 0.22

FRAME_MARGIN = 0.3

NEST_STEP = 0.05

FONT_TITLE = 10

FONT_HEAD = 7.4

FONT_LABEL = 7.2

FONT_FRAME = 6.8

# Ancho medio de un carácter en pulgadas, por punto de letra
# (DejaVu Sans; la negrita es más ancha).
CHAR_WIDTH = 0.6 / 72

BOLD_CHAR_WIDTH = 0.68 / 72


def _text_width(text, font_size, bold=False):

    return len(text) * font_size * (BOLD_CHAR_WIDTH if bold else CHAR_WIDTH)


def _fit_font(text, width, font_size, minimum, bold=False):

    # Letra más chica hasta que el texto quepa (con un mínimo).
    needed = _text_width(text, font_size, bold)

    if needed <= width:
        return font_size

    return max(minimum, font_size * width / needed)


def _chars_for(width, font_size):

    return max(8, int(width / (font_size * CHAR_WIDTH)))


# =========================================================
# EVENTS
# =========================================================
#
#   {"type": "msg", "src", "dst", "label", "dashed"}
#   {"type": "note", "at", "text"}
#   {"type": "frame", "kind", "label", "sections": [
#        {"guard", "events"}, ...]}
# =========================================================

def _msg(src, dst, label, dashed=False):

    return {
        "type": "msg",
        "src": src,
        "dst": dst,
        "label": label,
        "dashed": dashed
    }


def _note(at, text):

    return {
        "type": "note",
        "at": at,
        "text": text
    }


def _frame(kind, label, sections):

    sections = [
        section
        for section in sections
        if section["events"]
    ]

    if not sections:
        return None

    return {
        "type": "frame",
        "kind": kind,
        "label": label,
        "sections": sections
    }


def _short(text, limit):

    text = " ".join(str(text or "").split())

    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _wrap(text, width):

    words = []

    for word in str(text).split():

        # NOMBRE_LARGO_CON_GUIONES -> se parte por "_".
        while len(word) > width and "_" in word[1:width]:

            cut = word.rfind("_", 1, width) + 1

            words.append(word[:cut])

            word = word[cut:]

        words.append(word)

    lines = []

    current = ""

    for word in words:

        candidate = f"{current} {word}".strip()

        if len(candidate) > width and current:
            lines.append(current)
            current = word
        else:
            current = candidate

    if current:
        lines.append(current)

    return lines or [""]


# =========================================================
# MEASURE
# =========================================================

def _events_height(events):

    height = 0

    for event in events:

        if event["type"] == "msg":

            height += MSG_HEIGHT

        elif event["type"] == "note":

            height += NOTE_HEIGHT

        else:

            height += FRAME_TOP + FRAME_BOTTOM

            for index, section in enumerate(event["sections"]):

                if index:
                    height += SECTION_GAP

                height += _events_height(section["events"])

    return height


def _participants_in(events):

    found = set()

    for event in events:

        if event["type"] == "msg":

            found.update((event["src"], event["dst"]))

        elif event["type"] == "note":

            found.add(event["at"])

        else:

            for section in event["sections"]:
                found.update(_participants_in(section["events"]))

    return found


def _count_messages(events):

    total = 0

    for event in events:

        if event["type"] == "msg" and not event["dashed"]:
            total += 1

        elif event["type"] == "frame":

            for section in event["sections"]:
                total += _count_messages(section["events"])

    return total


# =========================================================
# SPLIT
# =========================================================
#
# Corta la lista de eventos de primer nivel en partes que
# quepan en una página. Nunca corta dentro de un loop/alt; un
# bloque más alto que una página va solo en su parte.
# =========================================================

def _split_events(events):

    body_max = (
        PAGE_HEIGHT
        - TITLE_HEIGHT
        - HEAD_HEIGHT
        - HEAD_GAP
        - BOTTOM_GAP
    )

    parts = [[]]

    height = 0

    for event in events:

        event_height = _events_height([event])

        if parts[-1] and height + event_height > body_max:

            parts.append([])

            height = 0

        parts[-1].append(event)

        height += event_height

    return parts


# =========================================================
# RENDER
# =========================================================

def _render_part(
    participants,
    events,
    title,
    first_number
):

    count = len(participants)

    column = min(1.9, (PAGE_WIDTH - 0.1) / count)

    width = column * count + 0.1

    def x_of(key):

        return 0.05 + column * (columns[key] + 0.5)

    columns = {
        participant["key"]: index
        for index, participant in enumerate(participants)
    }

    body = _events_height(events)

    height = TITLE_HEIGHT + HEAD_HEIGHT + HEAD_GAP + body + BOTTOM_GAP

    figure = plt.figure(
        figsize=(width, height),
        dpi=DPI
    )

    ax = figure.add_axes([0, 0, 1, 1])

    ax.set_xlim(0, width)

    ax.set_ylim(0, height)

    ax.axis("off")

    title_font = _fit_font(title, (width - 0.15) * 0.95, FONT_TITLE, 6.5, bold=True)

    title = _short(
        title,
        int((width - 0.15) / (title_font * BOLD_CHAR_WIDTH))
    )

    ax.text(
        width / 2,
        height - TITLE_HEIGHT / 2,
        title,
        ha="center",
        va="center",
        fontsize=title_font,
        fontweight="bold",
        color="#111111"
    )

    # -----------------------------------------------------
    # PARTICIPANTS + LIFELINES
    # -----------------------------------------------------

    head_top = height - TITLE_HEIGHT

    box_width = column - 0.08

    chars = max(8, int((box_width - 0.08) / (FONT_HEAD * BOLD_CHAR_WIDTH)))

    head_lines = {}

    for participant in participants:

        lines = _wrap(participant["title"], chars)

        if len(lines) > 3:
            lines = lines[:2] + [_short(" ".join(lines[2:]), chars)]

        head_lines[participant["key"]] = lines

    font_size = min(
        [FONT_HEAD]
        + [
            (box_width - 0.08) / (len(line) * BOLD_CHAR_WIDTH)
            for lines in head_lines.values()
            for line in lines
            if line
        ]
    )

    for participant in participants:

        x = x_of(participant["key"])

        lines = head_lines[participant["key"]]

        ax.add_patch(
            FancyBboxPatch(
                (x - box_width / 2, head_top - HEAD_HEIGHT),
                box_width,
                HEAD_HEIGHT,
                boxstyle="round,pad=0,rounding_size=0.04",
                linewidth=1.3,
                edgecolor=EDGE_DARK,
                facecolor=participant["color"],
                zorder=3
            )
        )

        ax.text(
            x,
            head_top - HEAD_HEIGHT / 2,
            "\n".join(lines),
            ha="center",
            va="center",
            fontsize=font_size,
            fontweight="bold",
            linespacing=1.1,
            color="#1E1E1E" if participant.get("dark_text") else "white",
            zorder=4
        )

        ax.plot(
            [x, x],
            [head_top - HEAD_HEIGHT, BOTTOM_GAP / 2],
            color=LIFELINE_COLOR,
            linewidth=0.9,
            linestyle=(0, (4, 3)),
            zorder=1
        )

    # -----------------------------------------------------
    # EVENTS
    # -----------------------------------------------------

    counter = [first_number - 1]

    def color_of(key):

        for participant in participants:

            if participant["key"] == key:
                return participant.get("arrow", participant["color"])

        return EDGE_DARK

    def place_label(text, center, font_size):

        # Centra el texto en la flecha sin salirse de la imagen.
        text = _short(text, _chars_for(width - 0.1, font_size))

        half = _text_width(text, font_size) / 2

        center = min(max(center, half + 0.05), width - half - 0.05)

        return text, center

    def draw_msg(event, y):

        src = event["src"]

        dst = event["dst"]

        label = event["label"]

        if not event["dashed"]:

            counter[0] += 1

            label = f"{counter[0]}. {label}"

        other = src if dst == "oic" else dst

        color = color_of(other if other != "oic" else src)

        y_arrow = y - MSG_HEIGHT + 0.07

        if src == dst:

            x = x_of(src)

            top = y_arrow + 0.1

            ax.plot(
                [x, x + 0.16, x + 0.16],
                [top, top, y_arrow],
                color=color,
                linewidth=1.1,
                zorder=5
            )

            ax.add_patch(
                FancyArrowPatch(
                    (x + 0.16, y_arrow),
                    (x + 0.01, y_arrow),
                    arrowstyle="-|>",
                    mutation_scale=7,
                    linewidth=1.1,
                    color=color,
                    shrinkA=0,
                    shrinkB=0,
                    zorder=5
                )
            )

            text, _center = place_label(label, x, FONT_LABEL)

            ax.text(
                x + 0.22,
                y_arrow + 0.05,
                text,
                ha="left",
                va="center",
                fontsize=FONT_LABEL,
                color="#222222",
                zorder=6
            )

            return

        x1 = x_of(src)

        x2 = x_of(dst)

        ax.add_patch(
            FancyArrowPatch(
                (x1, y_arrow),
                (x2, y_arrow),
                arrowstyle="-|>",
                mutation_scale=8,
                linewidth=1.1,
                linestyle=(0, (3, 2)) if event["dashed"] else "solid",
                color=color,
                shrinkA=0,
                shrinkB=1,
                zorder=5
            )
        )

        text, center = place_label(label, (x1 + x2) / 2, FONT_LABEL)

        ax.text(
            center,
            y_arrow + 0.1,
            text,
            ha="center",
            va="center",
            fontsize=FONT_LABEL,
            color="#222222",
            zorder=6,
            bbox={
                "boxstyle": "round,pad=0.08",
                "facecolor": "white",
                "edgecolor": "none",
                "alpha": 0.88
            }
        )

    def draw_note(event, y, bounds):

        x = x_of(event["at"])

        text = event["text"]

        max_width = bounds[1] - x - 0.1

        text = _short(text, _chars_for(max_width - 0.1, FONT_FRAME))

        note_width = _text_width(text, FONT_FRAME) + 0.14

        ax.add_patch(
            FancyBboxPatch(
                (x + 0.04, y - NOTE_HEIGHT + 0.05),
                note_width,
                NOTE_HEIGHT - 0.09,
                boxstyle="round,pad=0,rounding_size=0.03",
                linewidth=0.8,
                edgecolor=FRAME_COLOR,
                facecolor=NOTE_COLOR,
                zorder=4
            )
        )

        ax.text(
            x + 0.11,
            y - NOTE_HEIGHT / 2 + 0.01,
            text,
            ha="left",
            va="center",
            fontsize=FONT_FRAME,
            fontstyle="italic",
            color="#444444",
            zorder=5
        )

    def draw_events(events, y, depth, bounds=None):

        bounds = bounds or (0.02, width - 0.02)

        for event in events:

            if event["type"] == "msg":

                draw_msg(event, y)

                y -= MSG_HEIGHT

                continue

            if event["type"] == "note":

                draw_note(event, y, bounds)

                y -= NOTE_HEIGHT

                continue

            frame_height = _events_height([event])

            keys = _participants_in(
                [section_event
                 for section in event["sections"]
                 for section_event in section["events"]]
            )

            xs = [x_of(key) for key in keys]

            inset = NEST_STEP * depth

            left = max(bounds[0] + (0.04 if depth else 0), min(xs) - FRAME_MARGIN + inset)

            header_text = " ".join(
                part
                for part in (event["label"], event["sections"][0]["guard"])
                if part
            )

            tag_width = 0.42

            right = min(
                bounds[1] - (0.04 if depth else 0),
                max(
                    max(xs) + FRAME_MARGIN - inset,
                    left + tag_width + 0.12 + _text_width(header_text, FONT_FRAME)
                )
            )

            ax.add_patch(
                Rectangle(
                    (left, y - frame_height + 0.02),
                    right - left,
                    frame_height - 0.04,
                    fill=False,
                    edgecolor=FRAME_COLOR,
                    linewidth=0.9,
                    zorder=2
                )
            )

            tag_top = y - 0.02

            ax.add_patch(
                Rectangle(
                    (left, tag_top - 0.16),
                    tag_width,
                    0.16,
                    facecolor="#EFEFEF",
                    edgecolor=FRAME_COLOR,
                    linewidth=0.8,
                    zorder=3
                )
            )

            ax.text(
                left + tag_width / 2,
                tag_top - 0.08,
                event["kind"],
                ha="center",
                va="center",
                fontsize=FONT_FRAME,
                fontstyle="italic",
                fontweight="bold",
                color="#444444",
                zorder=4
            )

            ax.text(
                left + tag_width + 0.06,
                tag_top - 0.08,
                _short(
                    header_text,
                    _chars_for(right - left - tag_width - 0.1, FONT_FRAME)
                ),
                ha="left",
                va="center",
                fontsize=FONT_FRAME,
                color="#444444",
                zorder=4
            )

            y_inner = y - FRAME_TOP

            for index, section in enumerate(event["sections"]):

                if index:

                    ax.plot(
                        [left, right],
                        [y_inner - 0.03, y_inner - 0.03],
                        color=FRAME_COLOR,
                        linewidth=0.8,
                        linestyle=(0, (4, 2)),
                        zorder=2
                    )

                    ax.text(
                        left + 0.06,
                        y_inner - 0.12,
                        _short(section["guard"], _chars_for(right - left - 0.1, FONT_FRAME)),
                        ha="left",
                        va="center",
                        fontsize=FONT_FRAME,
                        color="#444444",
                        zorder=4
                    )

                    y_inner -= SECTION_GAP

                y_inner = draw_events(
                    section["events"],
                    y_inner,
                    depth + 1,
                    (left, right)
                )

            y -= frame_height

        return y

    draw_events(
        events,
        head_top - HEAD_HEIGHT - HEAD_GAP,
        0
    )

    png_file = os.path.join(
        tempfile.mkdtemp(),
        "secuencia.png"
    )

    figure.savefig(
        png_file,
        dpi=DPI,
        facecolor="white"
    )

    plt.close(figure)

    return png_file


def render_sequence_diagram(
    participants,
    events,
    title
):

    # Devuelve una lista de imágenes: una por parte.
    if not events:
        return []

    parts = _split_events(events)

    images = []

    number = 1

    for index, part in enumerate(parts, start=1):

        part_title = (
            f"{title} (parte {index} de {len(parts)})"
            if len(parts) > 1
            else title
        )

        images.append(
            _render_part(participants, part, part_title, number)
        )

        number += _count_messages(part)

    return images


# =========================================================
# GENERAL (2.4)
# =========================================================

def build_general_sequence(model):

    # Se recorre el grafo de relaciones del diagrama de
    # componentes a partir de los actores (Usuario, Scheduler,
    # Clientes REST): primero lo que ellos disparan y luego lo
    # que cada elemento llama, en el orden típico de uso. Sirve
    # para cualquier combinación de insumos (OIC, BIP, VB, BD).
    elements = model["elements"]

    relations = model["relations"]

    order = (
        model["top"]
        + ([model["hub"]] if model["hub"] else [])
        + model["bottom"]
    )

    position = {key: index for index, key in enumerate(order)}

    outgoing = {}

    for relation in relations:
        outgoing.setdefault(relation["src"], []).append(relation)

    for items in outgoing.values():
        items.sort(key=lambda relation: position.get(relation["dst"], 99))

    events = []

    visited_relations = set()

    queue = [
        key for key in model["top"]
        if elements[key]["kind"] == "actor"
    ]

    # Si no hay actores (p. ej. solo SQL), se parte del centro.
    if not queue and model["hub"]:
        queue = [model["hub"]]

    seen = set(queue)

    while queue:

        key = queue.pop(0)

        for relation in outgoing.get(key, []):

            pair = (relation["src"], relation["dst"])

            if pair in visited_relations:
                continue

            visited_relations.add(pair)

            events.append(_msg(relation["src"], relation["dst"], relation["label"]))

            if relation["dst"] not in seen:
                seen.add(relation["dst"])
                queue.append(relation["dst"])

    # Relaciones que no se alcanzan desde un actor.
    for relation in relations:

        pair = (relation["src"], relation["dst"])

        if pair not in visited_relations:
            events.append(_msg(relation["src"], relation["dst"], relation["label"]))

    if model.get("internal_calls") and "oic" in elements:

        events.append(
            _msg(
                "oic",
                "oic",
                "Invoca otras integraciones (p. ej. notificación de errores)"
            )
        )

    # Respuestas que sí aportan información (UML): lo que recibe
    # quien inició la interacción.
    replies = {
        "rest": "Respuesta del endpoint",
        "user": "Devuelve la información (pantalla o reporte)"
    }

    for relation in relations:

        reply = replies.get(relation["src"])

        if reply:
            events.append(_msg(relation["dst"], relation["src"], reply, dashed=True))

    participants = [
        {
            "key": key,
            "title": elements[key]["title"],
            "color": elements[key]["color"],
            "dark_text": elements[key].get("dark_text", False),
            **({"arrow": EDGE_DARK} if elements[key]["kind"] == "actor" else {})
        }
        for key in order
    ]

    return participants, events


def generate_general_sequence_diagram(model, title):

    # Devuelve una lista de imágenes (normalmente una). Sin
    # relaciones entre componentes no hay secuencia que mostrar.
    if not model or not model.get("relations"):
        return []

    participants, events = build_general_sequence(model)

    # Solo participan los elementos que tienen algún mensaje; los
    # que no tienen relación ya se ven en el de componentes.
    used = _participants_in(events)

    participants = [
        participant
        for participant in participants
        if participant["key"] in used
    ]

    return render_sequence_diagram(
        participants,
        events,
        title
    )


# =========================================================
# PER INTEGRATION (2.5)
# =========================================================

FOR_PATTERN = re.compile(r"recorre cada elemento de (\S+)")

GUARD_PATTERN = re.compile(r"si se cumple: (.+)$")

BRANCH_NAME_PATTERN = re.compile(r"^Rama (\w+)")

SCOPE_PATTERN = re.compile(r"^Scope (\S+)")


def _apps_in(items):

    for current in items:

        if current["kind"] == "invoke":
            yield current.get("app") or {}

        yield from _apps_in(current["children"])


def _iterated_names(items):

    # Nombres que recorre algún For ("por cada elemento de X").
    names = set()

    for current in items:

        if current["kind"] == "block" and current["text"].startswith("For"):

            match = FOR_PATTERN.search(current["text"])

            if match:
                names.add(match.group(1))

        names.update(_iterated_names(current["children"]))

    return names


def _connection_key(app):

    if app.get("IsIntegration"):
        return f"int:{app.get('IntegrationCode', '')}"

    return f"con:{app.get('ConnectionName') or app.get('Invoke') or 'Servicio'}"


def build_integration_sequence(
    tree,
    scheduled,
    endpoint_name="",
    integration_title="Integración",
    source_title="Cliente REST",
    extracted_iar=None
):

    # Retornos: solo cuando el resultado de una llamada se usa
    # después (lo recorre un For) o es la respuesta al cliente.
    iterated = _iterated_names(tree)

    apps = list(_apps_in(tree))

    prefix = _common_prefix_words(
        [integration_title]
        + ([] if scheduled else [source_title])
        + [
            app.get("ConnectionName") or ""
            for app in apps
            if not app.get("IsIntegration")
        ]
    )

    # Muchas conexiones: una línea de vida por sistema.
    grouped = (
        len({_connection_key(app) for app in apps}) + 2 > MAX_PARTICIPANTS
    )

    participants = [
        {
            "key": "trigger",
            "title": (
                "Scheduler OIC"
                if scheduled
                else _strip_prefix(source_title, prefix)
            ),
            "color": SOURCE_COLOR,
            "arrow": EDGE_DARK,
            "dark_text": True
        },
        {
            "key": "oic",
            "title": integration_title,
            "color": OIC_COLOR
        }
    ]

    seen = {"trigger", "oic"}

    def add_participant(key, title, color):

        if key not in seen:

            seen.add(key)

            participants.append({
                "key": key,
                "title": title,
                "color": color
            })

        return key

    def participant_for(app):

        # Devuelve (clave del participante, nombre a poner en la
        # etiqueta si la línea de vida es un grupo).
        if app.get("IsIntegration"):

            code = app.get("IntegrationCode") or "Integración"

            if grouped:
                return add_participant(
                    "int:*",
                    "Otras integraciones OIC",
                    INTEGRATION_CALL_COLOR
                ), code

            return add_participant(
                f"int:{code}",
                code,
                INTEGRATION_CALL_COLOR
            ), ""

        name = app.get("ConnectionName") or app.get("Invoke") or "Servicio"

        category = CATEGORY_BY_KEY[
            classify_connection(name, app.get("Tipo"))
        ]

        if grouped:
            return add_participant(
                f"cat:{category['key']}",
                category["title"],
                category["color"]
            ), _strip_prefix(name, prefix)

        return add_participant(
            f"con:{name}",
            _strip_prefix(name, prefix),
            category["color"]
        ), ""

    def operation_of(app):

        if not extracted_iar:
            return ""

        try:
            return endpoint_details(extracted_iar, app).get("operation", "")
        except Exception:
            return ""

    def compact_error(events, label):

        # Un bloque de error que solo llama a integraciones de
        # notificación o envía correo se resume en una nota.
        if not all(
            event["type"] == "msg"
            and (event["dst"].startswith("int:") or event["dst"] == "mail")
            for event in events
        ):
            return None

        targets = []

        for event in events:

            name = event.get("target_name") or event["label"].split(" · ")[0]

            if name not in targets:
                targets.append(name)

        return _note("oic", f"si falla: notifica a {', '.join(targets)}")

    def convert(items, scope_name=""):

        events = []

        for current in items:

            kind = current["kind"]

            text = current.get("text", "")

            if kind == "invoke":

                app = current.get("app") or {}

                target, group_name = participant_for(app)

                invoke_name = app.get("Invoke") or "Llamada"

                label = f"{group_name}: {invoke_name}" if group_name else invoke_name

                operation = operation_of(app)

                if operation:
                    label += f" · {operation}"

                message = _msg("oic", target, label)

                message["target_name"] = (
                    app.get("IntegrationCode")
                    if app.get("IsIntegration")
                    else invoke_name
                )

                events.append(message)

                if invoke_name in iterated:

                    events.append(
                        _msg(target, "oic", f"devuelve {invoke_name}", dashed=True)
                    )

            elif kind == "simple" and text.startswith("Envío de notificación"):

                add_participant("mail", "Servidor de correo", MAIL_COLOR)

                message = _msg("oic", "mail", "Envía correo")

                message["target_name"] = "correo"

                events.append(message)

            elif kind == "simple" and text.startswith("Reply"):

                events.append(_msg("oic", "trigger", "Respuesta", dashed=True))

            elif kind == "block":

                frame = None

                if text.startswith("For"):

                    match = FOR_PATTERN.search(text)

                    label = (
                        f"por cada elemento de {match.group(1)}"
                        if match
                        else "por cada elemento"
                    )

                    if "paralela" in text:
                        label += " (en paralelo)"

                    frame = _frame(
                        "loop",
                        label,
                        [{"guard": "", "events": convert(current["children"])}]
                    )

                elif text.startswith("While"):

                    guard = GUARD_PATTERN.search(text)

                    frame = _frame(
                        "loop",
                        "mientras " + (
                            guard.group(1) if guard else "se cumpla una condición"
                        ),
                        [{"guard": "", "events": convert(current["children"])}]
                    )

                elif text.startswith("Switch"):

                    sections = []

                    for branch in current["children"]:

                        branch_text = branch.get("text", "")

                        if branch_text.startswith("En cualquier otro caso"):

                            guard = "[en otro caso]"

                        else:

                            condition = GUARD_PATTERN.search(branch_text)

                            name = BRANCH_NAME_PATTERN.search(branch_text)

                            guard = "[" + (
                                condition.group(1)
                                if condition
                                else (name.group(1) if name else "condición")
                            ) + "]"

                        sections.append({
                            "guard": guard,
                            "events": convert(branch["children"])
                        })

                    non_empty = [section for section in sections if section["events"]]

                    frame = _frame(
                        "alt" if len(non_empty) > 1 else "opt",
                        "",
                        sections
                    )

                elif text.startswith(("Si ocurre un error", "Manejo global")):

                    label = (
                        "si falla cualquier paso"
                        if text.startswith("Manejo global")
                        else f"si falla {scope_name}".strip()
                    )

                    inner = convert(current["children"])

                    frame = (
                        compact_error(inner, label)
                        or _frame("error", label, [{"guard": "", "events": inner}])
                    ) if inner else None

                elif text.startswith("Scope"):

                    match = SCOPE_PATTERN.search(text)

                    events.extend(
                        convert(
                            current["children"],
                            match.group(1) if match else "el bloque"
                        )
                    )

                if frame:
                    events.append(frame)

        return events

    first_label = (
        "Dispara por horario"
        if scheduled
        else f"Invoca {endpoint_name}".strip()
    )

    events = [_msg("trigger", "oic", first_label)] + convert(tree)

    return participants, events


def generate_integration_sequence_diagram(
    tree,
    scheduled,
    title,
    endpoint_name="",
    integration_title="Integración",
    source_title="Cliente REST",
    extracted_iar=None
):

    # Devuelve una lista de imágenes: una por parte.
    participants, events = build_integration_sequence(
        tree,
        scheduled,
        endpoint_name=endpoint_name,
        integration_title=integration_title,
        source_title=source_title,
        extracted_iar=extracted_iar
    )

    return render_sequence_diagram(
        participants,
        events,
        title
    )
