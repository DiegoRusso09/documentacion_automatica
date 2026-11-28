# =========================================================
# FILE:
# oic_doc_generator/backend/parsers/vbs_backend_parser.py
# =========================================================
#
# Detecta los backends de una extensión de Visual Builder
# Studio (App UI de Oracle Fusion) a partir del .zip
# exportado, para el manual de instalación (IM090).
#
#   <ext>/sources/extension.json            id, nombre, versión
#   <ext>/sources/ui/self/applications/<app>/app.json
#   <ext>/sources/services/self/catalog.json  backends
#   <ext>/sources/services/self/<svc>/openapi3.json
#
# El zip NO guarda credenciales ni, para servidores locales
# (servers: []), el método de autenticación: esos datos
# viven en el ambiente de VB Studio y en "Manage Backends
# for Visual Builder Studio" del ERP. Por eso el usuario
# elige la autenticación en el diálogo del IM090.
# =========================================================

import json
import os
import re
import zipfile


# Métodos de autenticación de un backend de VB Studio.
# kind: fixed (credenciales fijas), identity (propagación
# de identidad), code_grant, none.
AUTH_METHODS = [
    {
        "key": "oracle_cloud_account",
        "label": "Oracle Cloud Account",
        "kind": "identity",
        "fields": []
    },
    {
        "key": "oauth2_user_assertion",
        "label": "OAuth 2.0 User Assertion",
        "kind": "identity",
        "fields": ["Scope"]
    },
    {
        "key": "basic",
        "label": "Basic Authentication",
        "kind": "fixed",
        "fields": ["Username", "Password"]
    },
    {
        "key": "oauth2_client_credentials",
        "label": "OAuth 2.0 Client Credentials",
        "kind": "fixed",
        "fields": ["Client ID", "Client Secret", "Token URL", "Scope"]
    },
    {
        "key": "oauth2_resource_owner",
        "label": "OAuth 2.0 Resource Owner Password Credentials",
        "kind": "fixed",
        "fields": [
            "Client ID", "Client Secret", "Token URL", "Scope",
            "Username", "Password"
        ]
    },
    {
        "key": "oauth2_code_grant",
        "label": "OAuth 2.0 Authorization Code Grant",
        "kind": "code_grant",
        "fields": [
            "Client ID", "Client Secret", "Authorization URL",
            "Token URL", "Scope"
        ]
    },
    {
        "key": "oci_signature",
        "label": "OCI Signature Authentication",
        "kind": "fixed",
        "fields": [
            "Tenancy OCID", "User OCID", "Fingerprint", "Private Key"
        ]
    },
    {
        "key": "none",
        "label": "Ninguna (None)",
        "kind": "none",
        "fields": []
    }
]

AUTH_BY_KEY = {
    method["key"]: method
    for method in AUTH_METHODS
}

# Valores que VB Studio escribe en x-vb.authentication de un
# servidor in-source -> clave de AUTH_METHODS.
_SOURCE_AUTH_ALIASES = {
    "oauth2_user_assertion": "oauth2_user_assertion",
    "oracle_cloud_account": "oracle_cloud_account",
    "oraclecloud": "oracle_cloud_account",
    "oracle_cloud": "oracle_cloud_account",
    "basic": "basic",
    "oauth2_client_credentials": "oauth2_client_credentials",
    "oauth2_resource_owner_password_credentials": "oauth2_resource_owner",
    "oauth2_resource_owner": "oauth2_resource_owner",
    "oauth2_code": "oauth2_code_grant",
    "oauth2_authorization_code": "oauth2_code_grant",
    "oci_signature": "oci_signature",
    "none": "none",
    "anonymous": "none"
}

CATALOG_PATTERN = re.compile(
    r"(?:^|/)sources/services/self/catalog\.json$"
)

EXTENSION_PATTERN = re.compile(
    r"(?:^|/)sources/extension\.json$"
)

APP_PATTERN = re.compile(
    r"(?:^|/)sources/ui/self/applications/([^/]+)/app\.json$"
)

PAGE_PATTERN = re.compile(
    r"(?:^|/)sources/ui/self/applications/([^/]+)/flows/[^/]+/pages/"
    r"([^/]+-page)\.json$"
)

SERVICE_PATTERN = re.compile(
    r"(?:^|/)sources/services/self/([^/]+)/openapi3\.json$"
)

# vb-catalog://backends/site_App:ics
# vb-catalog://backends/base:fscmRest/11.13.18.05:{...}
CATALOG_URL_PATTERN = re.compile(
    r"vb-catalog://backends/(?:([^:/]+):)?([^/]+)"
)

# Backends del propio ERP que ya vienen configurados.
BASE_NAMESPACE = "base"

# Nombre que muestra VB Studio cuando el catálogo no trae
# descripción.
DEFAULT_BACKEND_LABELS = {
    "ics": "Integration Applications",
    "custom": "Custom Applications",
    "pcs": "Process Applications"
}


def _read_json(archive, name):

    try:
        data = json.loads(
            archive.read(name).decode("utf-8", "ignore")
        )
    except (KeyError, ValueError):
        return {}

    return data if isinstance(data, dict) else {}


def _open(uploaded):

    if hasattr(uploaded, "seek"):
        uploaded.seek(0)

    source = (
        os.fspath(uploaded)
        if isinstance(uploaded, (str, os.PathLike))
        else uploaded
    )

    return zipfile.ZipFile(source)


def _file_name(uploaded):

    name = getattr(uploaded, "name", None) or (
        os.fspath(uploaded)
        if isinstance(uploaded, (str, os.PathLike))
        else "aplicacion.zip"
    )

    return os.path.basename(str(name))


def _servers_auth(servers):

    # Autenticación de un servidor in-source, si la trae.
    for server in servers or []:

        authentication = (
            (server.get("x-vb") or {}).get("authentication") or {}
        )

        for key in ("authenticated", "anonymous"):

            auth = authentication.get(key)

            if isinstance(auth, dict) and auth.get("type"):

                raw = str(auth["type"])

                return (
                    _SOURCE_AUTH_ALIASES.get(raw.lower()),
                    raw
                )

    return (None, None)


def _service_backends(spec):

    # (namespace, backend) de los servidores de un servicio
    result = []

    for server in spec.get("servers") or []:

        match = CATALOG_URL_PATTERN.search(server.get("url", ""))

        if match:
            result.append((match.group(1) or "", match.group(2)))

    return result


def analyze_vbs_backends(uploaded):

    # Devuelve los datos de la extensión y sus backends.
    result = {
        "file_name": _file_name(uploaded),
        "layout": None,
        "extension_id": "",
        "extension_name": "",
        "extension_version": "",
        "applications": [],
        "backends": [],
        "base_backends": [],
        "erp_services": [],
        "warnings": []
    }

    try:

        with _open(uploaded) as archive:

            names = archive.namelist()

            catalog_name = next(
                (n for n in names if CATALOG_PATTERN.search(n)),
                None
            )

            if not catalog_name:

                result["layout"] = (
                    "classic"
                    if any("/webApps/" in f"/{n}" for n in names)
                    else None
                )

                return result

            result["layout"] = "extension"

            extension_name = next(
                (n for n in names if EXTENSION_PATTERN.search(n)),
                None
            )

            if extension_name:

                extension = _read_json(archive, extension_name)

                result["extension_id"] = extension.get("id", "")
                result["extension_name"] = extension.get("name", "")
                result["extension_version"] = str(
                    extension.get("version", "")
                )

            for name in names:

                match = APP_PATTERN.search(name)

                if not match:
                    continue

                app = _read_json(archive, name)

                result["applications"].append({
                    "id": app.get("id") or match.group(1),
                    "name": (
                        (app.get("unifiedAppSettings") or {})
                        .get("displayName")
                        or app.get("description")
                        or match.group(1)
                    )
                })

            pages = {}

            for name in names:

                match = PAGE_PATTERN.search(name)

                if match:
                    pages.setdefault(match.group(1), []).append(
                        match.group(2)
                    )

            for app in result["applications"]:
                app["pages"] = sorted(pages.get(app["id"], []))

            catalog = _read_json(archive, catalog_name)

            # Servicios que usa cada backend
            usage = {}

            for name in names:

                match = SERVICE_PATTERN.search(name)

                if not match:
                    continue

                spec = _read_json(archive, name)

                for namespace, backend in _service_backends(spec):
                    usage.setdefault(
                        (namespace, backend), []
                    ).append(match.group(1))

            for service, spec in (catalog.get("services") or {}).items():

                for namespace, backend in _service_backends(spec or {}):
                    usage.setdefault(
                        (namespace, backend), []
                    ).append(service)

            own = result["extension_id"]

            backends = catalog.get("backends") or {}

            for backend_id, definition in backends.items():

                definition = definition or {}

                servers = definition.get("servers") or []

                reference = None

                reference_namespace = None

                for server in servers:

                    match = CATALOG_URL_PATTERN.search(
                        server.get("url", "")
                    )

                    if match:
                        reference_namespace = match.group(1) or own
                        reference = match.group(2)
                        break

                detected, detected_raw = _servers_auth(servers)

                if not servers:
                    server_kind = "local"
                elif reference:
                    server_kind = "reference"
                else:
                    server_kind = "in_source"

                services = sorted(set(
                    usage.get((own, backend_id), [])
                    + usage.get(("", backend_id), [])
                ))

                description = (definition.get("description") or "").strip()

                result["backends"].append({
                    "id": backend_id,
                    "description": description,
                    # El nombre que se ve en VB Studio es la
                    # descripción (p. ej. ics -> Integration Applications)
                    "label": (
                        description
                        or DEFAULT_BACKEND_LABELS.get(backend_id)
                        or backend_id
                    ),
                    "service_type": definition.get("serviceType", ""),
                    "server_kind": server_kind,
                    "reference": reference,
                    "reference_namespace": reference_namespace,
                    "in_source_url": (
                        servers[0].get("url", "")
                        if server_kind == "in_source"
                        else ""
                    ),
                    "detected_auth": detected,
                    "detected_auth_raw": detected_raw,
                    "services": services
                })

                if reference and reference not in backends and services:
                    result["warnings"].append(
                        "El backend '"
                        + (
                            description
                            or DEFAULT_BACKEND_LABELS.get(backend_id)
                            or backend_id
                        )
                        + "' "
                        f"apunta a '{reference}', que no está definido "
                        "en el catálogo de la extensión: debe existir "
                        "en el ambiente destino."
                    )

            # Servicios del catálogo que van al ERP (fscmRest...)
            result["erp_services"] = sorted(
                service
                for service, spec in (catalog.get("services") or {}).items()
                if any(
                    namespace == BASE_NAMESPACE
                    for namespace, _ in _service_backends(spec or {})
                )
            )

            # Backends del ERP (base:fscmRest, base:hcmRest...)
            result["base_backends"] = sorted({
                backend
                for (namespace, backend) in usage
                if namespace == BASE_NAMESPACE
            })

    except zipfile.BadZipFile:

        result["warnings"].append("El archivo no es un .zip válido.")

    finally:

        if hasattr(uploaded, "seek"):
            try:
                uploaded.seek(0)
            except Exception:
                pass

    return result


def apply_auth_selection(analysis, selection):

    # selection: {backend_id: auth_key}. Si no se eligió, se
    # usa lo detectado en el código fuente (servidor in-source).
    selection = selection or {}

    for backend in analysis.get("backends", []):

        chosen = selection.get(backend["id"])

        if chosen not in AUTH_BY_KEY:
            chosen = backend.get("detected_auth")

        backend["auth"] = chosen if chosen in AUTH_BY_KEY else None

    return analysis
