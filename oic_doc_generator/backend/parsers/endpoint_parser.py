# =========================================================
# FILE: endpoint_parser.py
# =========================================================
#
# Detalle técnico de cada conexión que usa una integración,
# leído de los archivos .jca del .iar:
#
#   REST   -> método y ruta       POST /actualizarEstadoPedido/{id}
#   FTP    -> protocolo/operación SFTP ListFile *.txt
#   DBaaS  -> operación y objeto  Merge XX_CLIENTES
#   SOAP   -> operación           runReport
#
# Y los reportes BIP (.xdo) que la integración ejecuta, que
# aparecen en los mapeos (.xsl) de las llamadas a BI Publisher.
# =========================================================

import os
import re

from oic_doc_generator.backend.parsers.iar_parser import (
    find_application_folder
)

from oic_doc_generator.backend.parsers.connections_parser import (
    analyze_dbaas_jca
)


PROPERTY_PATTERN = re.compile(
    r'name="(\w+)"\s+value="([^"]*)"'
)

REPORT_PATTERN = re.compile(
    r"([^/\"'<>;&]+)\.xdo"
)


def _jca_properties(folder):

    properties = {}

    if not folder or not os.path.isdir(folder):
        return properties

    for root, _dirs, files in os.walk(folder):

        for name in files:

            if not name.endswith(".jca"):
                continue

            try:

                with open(
                    os.path.join(root, name),
                    encoding="utf-8",
                    errors="ignore"
                ) as file:

                    for key, value in PROPERTY_PATTERN.findall(file.read()):
                        properties.setdefault(key, value)

            except OSError:
                continue

    return properties


def endpoint_details(extracted_iar, app):

    # Devuelve {"operation", "detail", "verb"}:
    #   operation: texto corto para el diagrama.
    #   verb: acción genérica (consulta, registra, lee...)
    #         para etiquetar las relaciones.
    code = app.get("Codigo", "")

    folder = find_application_folder(extracted_iar, code) if code else None

    properties = _jca_properties(folder)

    kind = (app.get("Tipo") or "").upper()

    # REST
    if properties.get("ResourceURI") or properties.get("HttpVerb"):

        method = properties.get("HttpVerb", "").upper()

        path = properties.get("ResourceURI", "")

        return {
            "operation": f"{method} {path}".strip(),
            "verb": {
                "GET": "consulta",
                "POST": "registra",
                "PUT": "actualiza",
                "PATCH": "actualiza",
                "DELETE": "elimina"
            }.get(method, "invoca")
        }

    # FTP / SFTP
    if properties.get("FtpConnectionType") or kind == "FTP":

        operation = properties.get("Operation", "")

        files = properties.get("IncludeFilesWildCard", "")

        protocol = properties.get("FtpConnectionType", "FTP")

        lowered = operation.lower()

        return {
            "operation": " ".join(
                part for part in (protocol, operation, files) if part
            ),
            "verb": (
                "lista" if "list" in lowered
                else "lee" if "read" in lowered or "download" in lowered
                else "escribe" if "write" in lowered or "upload" in lowered
                else "mueve" if "move" in lowered
                else "elimina" if "delete" in lowered
                else "transfiere"
            )
        }

    # Base de datos
    if kind in ("DBAAS", "ATP", "DB", "ORACLE DB"):

        try:
            database = analyze_dbaas_jca(folder) if folder else {}
        except Exception:
            database = {}

        operation = database.get("Operacion", "")

        target = (
            ".".join(
                part
                for part in (database.get("Package"), database.get("Procedure"))
                if part
            )
            or database.get("Tabla", "")
        )

        lowered = operation.lower()

        return {
            "operation": " ".join(part for part in (operation, target) if part),
            "verb": (
                "consulta" if "select" in lowered
                else "ejecuta" if database.get("Procedure")
                else "escribe" if lowered
                else "usa"
            ),
            "table": database.get("Tabla", ""),
            "procedure": target if database.get("Procedure") else ""
        }

    # SOAP y otros adaptadores
    operation = properties.get("targetOperation", "")

    return {
        "operation": operation,
        "verb": (
            "ejecuta reportes" if operation == "runReport"
            else "invoca"
        )
    }


def report_names(extracted_iar):

    # Reportes BIP (.xdo) que aparecen en los mapeos.
    names = set()

    for root, _dirs, files in os.walk(extracted_iar):

        for name in files:

            if not name.endswith(".xsl"):
                continue

            try:

                with open(
                    os.path.join(root, name),
                    encoding="utf-8",
                    errors="ignore"
                ) as file:

                    text = file.read()

            except OSError:
                continue

            if ".xdo" not in text:
                continue

            for match in REPORT_PATTERN.findall(text):
                names.add(match.strip())

    return sorted(names)
