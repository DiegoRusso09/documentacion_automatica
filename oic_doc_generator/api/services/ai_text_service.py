# =========================================================
# FILE:
# oic_doc_generator/api/services/ai_text_service.py
# =========================================================

import os
import re

from oic_doc_generator.api.services import ai_providers


# =========================================================
# PROVIDERS
# =========================================================
#
# La elección de proveedor (Gemini, Groq, Cerebras...) y el
# paso al siguiente cuando uno falla están en ai_providers.
# =========================================================

AI_MAX_OUTPUT_TOKENS = int(
    os.getenv(
        "AI_MAX_OUTPUT_TOKENS",
        "4000"
    )
)

AI_VALIDATION_ATTEMPTS = 2


# =========================================================
# INSTRUCTIONS
# =========================================================

TECHNICAL_NARRATIVE_INSTRUCTIONS = """
Eres un arquitecto técnico especializado en Oracle Integration Cloud (OIC).

Recibirás el esquema de un flujo OIC generado automáticamente a partir
de la orquestación real de la integración. Es una lista jerárquica:
la sangría indica qué actividades están dentro de cada While, For,
Switch (cada rama con su condición), Scope o manejo de errores.

Tu tarea es escribir un RESUMEN CORTO de lo que hace el flujo, que
entienda tanto un perfil técnico como un usuario funcional.

REGLAS OBLIGATORIAS:

1. Un solo párrafo de entre 60 y 120 palabras. Nunca más de 120.

2. Cuenta la idea general del flujo en orden: cómo inicia, qué
   recorre o repite, qué decide y qué hace al final. No describas
   actividad por actividad.

3. Menciona por su nombre EXACTO cada conexión (por ejemplo
   getPayments, uploadAttachment) y cada integración invocada
   (por ejemplo ACME_FACTURA_PDF). No los traduzcas, corrijas
   ni modifiques, aunque parezcan tener errores de escritura.

4. NO incluyas: versiones, endpoints, operaciones HTTP, nombres de
   conectores de integraciones, cantidades de Assignment, Stitch o
   Logger, ni expresiones o condiciones literales.

5. Explica las decisiones en lenguaje claro y breve, por ejemplo
   "si no se encuentra el archivo, el flujo termina" o "según el
   tipo de pago". Si la condición es "una condición compleja", di
   solo "según una validación".

6. Respeta la estructura del esquema: no pongas una actividad dentro
   de un ciclo o rama distinta a la que indica la sangría.

7. El manejo de errores menciónalo en una frase corta como máximo,
   y solo si invoca alguna conexión o integración.

8. Usa los términos de OIC (For, While, Switch, Scope, stageFile)
   solo si ayudan; prefiere expresiones claras como "por cada pago",
   "reintenta hasta", "según el resultado".

9. No inventes actividades, conexiones ni propósitos: no deduzcas
   para qué sirve una conexión por su nombre.

10. Si escribes un número, debe aparecer tal cual en el esquema.

11. Devuelve solo el párrafo, en español, sin formato Markdown.
"""


# =========================================================
# NATURALIZE
# =========================================================


# =========================================================
# REQUIRED TERMS
# =========================================================
#
# Nombres que el resumen debe contener literalmente
# (conexiones y códigos de integración).
# Se extraen del esquema que arma orchestration_parser:
#
#   Conexión <TIPO> <nombre>
#   Llamada a la integración <CODIGO> versión <V>,
#   endpoint <RUTA> (<OP>), mediante el conector <nombre>
# =========================================================

CONNECTION_PATTERN = re.compile(
    r"Conexión \S+ (\S+)$",
    re.MULTILINE
)

INTEGRATION_PATTERN = re.compile(
    r"Llamada a la integración (\S+) versión (\S+), "
    r"endpoint (\S+) \(\S*\), mediante el conector (\S+)$",
    re.MULTILINE
)


NUMBER_PATTERN = re.compile(
    r"\d+"
)


# Identificadores técnicos (camelCase, con "_" o con dígitos):
# el texto en español normal no los contiene.
IDENTIFIER_PATTERN = re.compile(
    r"\b(?:[a-z]+[A-Z]\w*|\w*_\w+|[A-Za-z]+\d\w*)\b"
)

ERROR_HANDLER_PREFIXES = (
    "- Si ocurre un error",
    "- Manejo global de errores"
)


def main_flow_text(
    text: str
):

    # Quita las líneas de los bloques de manejo de errores
    # (y todo lo anidado bajo ellos) según la sangría.
    lines = []

    skip_indent = None

    for line in text.splitlines():

        indent = len(line) - len(line.lstrip())

        if skip_indent is not None and indent > skip_indent:
            continue

        skip_indent = None

        if line.strip().startswith(ERROR_HANDLER_PREFIXES):
            skip_indent = indent
            continue

        lines.append(line)

    return "\n".join(lines)


def extract_required_terms(
    text: str
):

    # Solo el flujo principal: el manejo de errores puede
    # omitirse en el resumen corto.
    main_text = main_flow_text(
        text
    )

    terms = set(
        CONNECTION_PATTERN.findall(main_text)
    )

    # Solo el código de la integración: versión, endpoint y
    # conector quedan fuera del resumen corto.
    for groups in INTEGRATION_PATTERN.findall(main_text):

        terms.add(groups[0])

    return terms

# =========================================================
# REQUEST
# =========================================================

def _request_naturalized_text(
    text: str
):

    # Tope de seguridad, muy por encima de un resumen normal
    # (60-120 palabras). Incluye el razonamiento interno de los
    # modelos que lo usan.
    result, _provider = ai_providers.complete(
        TECHNICAL_NARRATIVE_INSTRUCTIONS,
        text,
        AI_MAX_OUTPUT_TOKENS
    )

    return result


# =========================================================
# NATURALIZE
# =========================================================

def naturalize_technical_text(
    text: str
):

    text = (
        text
        or
        ""
    ).strip()


    if not text:

        raise ValueError(
            "El texto de entrada está vacío."
        )


    required_terms = extract_required_terms(
        text
    )


    missing = set()


    # =====================================================
    # VALIDATION
    # =====================================================
    #
    # Si la IA altera u omite un nombre técnico se reintenta
    # una vez; si vuelve a fallar se descarta el texto y el
    # llamador usa el esquema determinístico.
    # =====================================================

    request_text = text


    for attempt in range(1, AI_VALIDATION_ATTEMPTS + 1):

        result = _request_naturalized_text(
            request_text
        )


        if not result:

            raise RuntimeError(
                "La IA no devolvió texto."
            )


        # Palabra completa: "notification" no debe darse por
        # presente solo porque aparezca "notification1".
        missing = {
            term
            for term in required_terms
            if not re.search(
                r"(?<!\w)" + re.escape(term) + r"(?!\w)",
                result
            )
        }


        # Ningún identificador del resumen puede estar
        # alterado: debe existir tal cual en el esquema.
        missing.update(
            f"alterado {identifier}"
            for identifier in set(IDENTIFIER_PATTERN.findall(result))
            if not re.search(
                r"(?<!\w)" + re.escape(identifier) + r"(?!\w)",
                text
            )
        )


        # Todo número del resumen (cantidades, versiones,
        # valores de condiciones) debe existir en el esquema.
        missing.update(
            f"número {number}"
            for number in set(NUMBER_PATTERN.findall(result))
            - set(NUMBER_PATTERN.findall(text))
        )


        if not missing:

            return result


        print(
            f"[AI TEXT] Intento {attempt}: faltan o se alteraron",
            sorted(missing)
        )


        # El reintento le indica a la IA qué corregir.
        request_text = (
            text
            + "\n\nCORRECCIÓN: tu resumen anterior no cumplió las "
            "reglas. Escríbelo de nuevo con estos cambios: "
            + "; ".join(sorted(
                f"no uses {term[len('alterado '):]}, no existe en el esquema"
                if term.startswith("alterado ")
                else f"no escribas el {term}, no está en el esquema"
                if term.startswith("número ")
                else f"menciona exactamente {term}"
                for term in missing
            ))
            + "."
        )


    raise RuntimeError(
        "La IA alteró u omitió nombres técnicos: "
        + ", ".join(sorted(missing))
    )
