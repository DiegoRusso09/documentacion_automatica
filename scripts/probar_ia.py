# =========================================================
# FILE: scripts/probar_ia.py
# =========================================================
#
# Prueba aislada de la naturalización de texto del DS140,
# usando el mismo servicio de IA que la aplicación.
#
# Uso:
#   python scripts/probar_ia.py <archivo.iar | archivo.par | carpeta>
#   python scripts/probar_ia.py --texto "El endpoint X comienza con: ..."
#
# Sin proveedores configurados: muestra el texto exacto
# que se enviaría (no llama a ninguna IA).
#
# Con clave: llama a la IA y muestra la respuesta; el servicio
# imprime los tokens reales de cada llamada.
# =========================================================

import sys
import time
import zipfile
import tempfile

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT_DIR))

from oic_doc_generator.api.services import ai_providers

from oic_doc_generator.api.services.ai_text_service import (
    naturalize_technical_text
)

from oic_doc_generator.backend.parsers.iar_parser import (
    extract_iar
)

from oic_doc_generator.backend.parsers.par_parser import (
    find_all_iar_files
)

from oic_doc_generator.backend.parsers.project_parser import (
    get_project_name,
    read_project_xml,
    build_application_map,
    get_project_root
)

from oic_doc_generator.backend.parsers.orchestration_parser import (
    get_endpoint_flows,
    generate_description
)


# =========================================================
# COLLECT DESCRIPTIONS
# =========================================================

def find_iars(path):

    path = Path(path)

    if path.is_dir():

        return find_all_iar_files(str(path))

    if path.suffix.lower() == ".iar":

        return [str(path)]

    if path.suffix.lower() == ".par":

        temp_dir = tempfile.mkdtemp()

        with zipfile.ZipFile(path) as zip_ref:

            zip_ref.extractall(temp_dir)

        return find_all_iar_files(temp_dir)

    raise SystemExit(
        f"No reconozco el archivo: {path}"
    )


def collect_descriptions(path):

    descriptions = []

    for iar in find_iars(path):

        extracted_iar = extract_iar(iar)

        integration_name = get_project_name(extracted_iar)

        applications = read_project_xml(extracted_iar)

        app_map = build_application_map(applications)

        root = get_project_root(extracted_iar)

        flows = get_endpoint_flows(root, app_map)

        for endpoint, flow in flows.items():

            descriptions.append((
                f"{integration_name} / {endpoint}",
                generate_description(
                    endpoint,
                    flow,
                    applications,
                    extracted_iar,
                    root
                )
            ))

    return descriptions


# =========================================================
# MAIN
# =========================================================

def main():

    if len(sys.argv) < 2:

        raise SystemExit(
            "Uso: python scripts/probar_ia.py "
            "<archivo.iar | archivo.par | carpeta> "
            "| --texto \"...\""
        )

    if sys.argv[1] == "--texto":

        descriptions = [("texto manual", " ".join(sys.argv[2:]))]

    else:

        descriptions = collect_descriptions(sys.argv[1])

    print(
        f"IA: {ai_providers.describe()}"
    )

    for name, text in descriptions:

        print("=" * 70)
        print(f"ENDPOINT: {name}")
        print("-" * 70)
        print("SE ENVÍA:")
        print(text)

        if ai_providers.is_enabled():

            start = time.time()

            result = naturalize_technical_text(text)

            print("-" * 70)
            print(f"RESPUESTA ({time.time() - start:.1f}s):")
            print(result)

    print("=" * 70)
    print(
        f"TOTAL DOCUMENTO: {len(descriptions)} llamadas a la IA"
    )


if __name__ == "__main__":

    main()
