# =========================================================
# FILE: scripts/probar_proveedores.py
# =========================================================
#
# Comprueba cada proveedor de IA configurado (cada clave,
# incluidas las de respaldo, el modelo y la conexión) con una
# petición mínima, y muestra el uso de hoy.
#
# Uso:
#   python scripts/probar_proveedores.py
# =========================================================

import sys
import time

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from oic_doc_generator.api.services import ai_providers


def test_client(client, model):

    try:

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Responde solo: OK"}],
            max_tokens=200
        )

        return (
            "OK  respuesta="
            + repr((response.choices[0].message.content or "").strip()[:30])
        )

    except Exception as error:

        return f"ERROR {error!r:.300}"


def main():

    if not ai_providers.is_enabled():

        raise SystemExit(
            "No hay proveedores configurados. Copia "
            "ia_proveedores.ejemplo.json a ia_proveedores.json "
            "y rellena las claves."
        )

    usage = ai_providers.usage_today()

    for provider in ai_providers.PROVIDERS:

        name = provider["nombre"]

        tope = provider["tope_diario"] or "sin tope"

        print(
            f"{name}  modelo={provider['modelo']}  "
            f"usadas hoy={usage.get(name, 0)}/{tope}"
        )

        for number, client in enumerate(provider["clients"], start=1):

            label = "principal" if number == 1 else f"respaldo {number - 1}"

            start = time.time()

            status = test_client(client, provider["modelo"])

            print(f"   clave {label:11} {time.time() - start:4.1f}s  {status}")


if __name__ == "__main__":

    main()
