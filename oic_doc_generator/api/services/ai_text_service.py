# =========================================================
# FILE:
# oic_doc_generator/api/services/ai_text_service.py
# =========================================================

import os

from openai import OpenAI


# =========================================================
# CLIENT
# =========================================================

client = OpenAI(
    timeout=30.0,
    max_retries=1
)


# =========================================================
# MODEL
# =========================================================

AI_TEXT_MODEL = os.getenv(
    "OPENAI_TEXT_MODEL",
    "gpt-5.6-luna"
)


# =========================================================
# INSTRUCTIONS
# =========================================================

TECHNICAL_NARRATIVE_INSTRUCTIONS = """
Eres un arquitecto técnico especializado en Oracle Integration Cloud (OIC).

Recibirás una descripción técnica generada automáticamente a partir
de la orquestación real de una integración OIC.

Tu única responsabilidad es mejorar su redacción para convertirla
en una descripción técnica, natural, profesional y fluida.

REGLAS OBLIGATORIAS:

1. No inventes ninguna actividad, conexión, endpoint, variable,
   operación, condición, ciclo o funcionalidad.

2. No elimines ninguna actividad indicada en el texto original.

3. Conserva EXACTAMENTE los nombres técnicos recibidos.
   No traduzcas, corrijas ni modifiques nombres como:
   actualizarFlex, postToken, getPdf, leerCobro, etc.

4. Conserva los términos técnicos Oracle Integration Cloud,
   incluyendo cuando correspondan:
   REST, SOAP, stageFile, Assignment, Switch, While, For y Scope.

5. Mantén el orden de ejecución indicado en el texto original.

6. Cuando exista un For:
   - indica la colección sobre la cual itera;
   - conserva si la ejecución es secuencial o paralela.

7. Cuando exista un stageFile, conserva la operación indicada,
   por ejemplo Write o Read.

8. Evita frases repetitivas o mecánicas como:
   "se llama a",
   "ahora comienza",
   "se realiza",
   siempre que puedan reemplazarse por una redacción más natural.

9. Puedes utilizar expresiones como:
   "inicia",
   "a continuación",
   "posteriormente",
   "seguidamente",
   "el flujo continúa",
   "dentro de este ciclo",
   "finalmente".

10. No deduzcas el propósito funcional de una conexión por su nombre.
    Por ejemplo, si existe una conexión llamada getPdf,
    no afirmes que "obtiene el PDF" a menos que el texto original
    lo indique explícitamente.

11. No agregues introducciones, conclusiones ni recomendaciones.

12. Devuelve únicamente un párrafo técnico en español.
"""


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


    response = client.responses.create(

        model=
            AI_TEXT_MODEL,

        instructions=
            TECHNICAL_NARRATIVE_INSTRUCTIONS,

        input=
            text
    )


    result = (
        response.output_text
        or
        ""
    ).strip()


    if not result:

        raise RuntimeError(
            "OpenAI no devolvió texto."
        )


    return result