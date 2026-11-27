# =========================================================
# FILE: component_diagram_generator.py
# =========================================================
#
# Diagrama de componentes MAESTRO del desarrollo (sección 2.3
# del DS140): una sola imagen con todos los elementos.
#
#   Origen (izquierda)     Centro           Destinos (derecha)
#   Scheduler OIC   ──►                 ──► ERP Fusion Cloud
#   Clientes REST   ──►      OIC        ──► Base de datos
#   Visual Builder  ──►  (integraciones) ──► Servidor FTP
#   APEX            ──►                 ──► Servicios externos
#
# Sigue las reglas del modelo C4:
#   - cada elemento muestra nombre, tecnología y una frase;
#   - cada relación es UNA flecha en un sentido, con etiqueta
#     "qué hace [protocolo]";
#   - dentro de cada sistema se listan los servicios usados
#     (método y ruta REST, operación SFTP, tabla, reporte...).
#
# MODELO COMÚN: cada insumo del DS140 aporta elementos y
# relaciones a un mismo modelo; el dibujo no depende del tipo
# de insumo. Para un insumo nuevo basta con otro aportador.
#   - .iar/.par   -> integraciones, orígenes y sistemas destino
#   - VB / APEX   -> aplicaciones y a qué llaman (evidencia en
#                    sus archivos)
#   - BI Publisher-> reportes (en ERP); se marcan los que OIC
#                    ejecuta
#   - SQL         -> paquetes y tablas (en Base de datos); se
#                    marcan las tablas que OIC escribe/lee
# Las relaciones solo se dibujan con evidencia. Un elemento sin
# relación igual aparece, con la nota "sin relación detectada".
#
# Se dibuja con matplotlib (ya está en requirements.txt y trae
# su propia fuente con tildes, así funciona igual en Render).
# =========================================================

import json
import os
import re
import tempfile
import zipfile

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from matplotlib.patches import (
    FancyArrowPatch,
    FancyBboxPatch
)

from oic_doc_generator.backend.parsers.iar_parser import (
    find_all_iar_files,
    extract_iar
)

from oic_doc_generator.backend.parsers.project_parser import (
    build_application_map,
    get_project_name,
    get_project_root,
    get_project_version,
    read_project_xml
)

from oic_doc_generator.backend.parsers.orchestration_parser import (
    analyze_flow,
    get_endpoint_flows
)

from oic_doc_generator.backend.parsers.schedule_parser import (
    is_scheduled_integration
)

from oic_doc_generator.backend.parsers.endpoint_parser import (
    endpoint_details,
    report_names
)


# =========================================================
# CATEGORIES
# =========================================================
#
# Cada conexión de destino se agrupa en un sistema según su
# nombre y tipo. El orden importa: gana la primera regla.
# =========================================================

CATEGORIES = [

    {
        "key": "erp",
        "title": "ERP Fusion Cloud",
        "description": "Servicios de Oracle Fusion y reportes BI Publisher",
        "color": "#F0932B",
        "keywords": ("erp", "fusion", "bip", "otbi", "dff", "ess", "schedule")
    },

    {
        "key": "db",
        "title": "Base de datos",
        "description": "Datos y estados del proceso",
        "color": "#4F9BE0",
        "keywords": ("ords", "dbaas", " db", "atp", "adb", "database", "oracle db")
    },

    {
        "key": "ftp",
        "title": "Servidor de archivos",
        "description": "Intercambio de archivos",
        "color": "#3BAA6E",
        "keywords": ("ftp",)
    },

    {
        "key": "bo",
        "title": "Business Objects (VB)",
        "description": "Base de datos interna de Visual Builder",
        "color": "#5B8DB8",
        "keywords": ()
    },

    {
        "key": "apex",
        "title": "APEX",
        "description": "Aplicación APEX",
        "color": "#9B59B6",
        "keywords": ("apex",)
    },

    {
        "key": "other",
        "title": "Servicios externos",
        "description": "Servicios de terceros",
        "color": "#2BA6A6",
        "keywords": ()
    }
]

CATEGORY_BY_KEY = {
    category["key"]: category
    for category in CATEGORIES
}

OIC_COLOR = "#D9534F"

SOURCE_COLOR = "#E8ECEF"

INNER_COLOR = "#FCF3C8"

EDGE_DARK = "#333333"

# Operaciones listadas por conexión dentro de cada sistema.
MAX_OPERATIONS = 3


def classify_connection(connection_name, connection_type):

    text = f" {connection_name or ''} {connection_type or ''} ".lower()

    for category in CATEGORIES:

        if any(keyword in text for keyword in category["keywords"]):
            return category["key"]

    return "other"


# =========================================================
# HELPERS
# =========================================================

def _file_label(uploaded):

    name = getattr(uploaded, "name", None) or getattr(uploaded, "filename", None)

    if not name and isinstance(uploaded, (str, os.PathLike)):
        name = os.fspath(uploaded)

    base = os.path.basename(str(name or "")).strip()

    return os.path.splitext(base)[0] or "Aplicación"


def _common_prefix_words(names):

    # "ACME Ventas ORDS", "ACME Ventas FTP"
    # -> "ACME Ventas": se quita para que las cajas no
    # repitan lo mismo en cada línea.
    split = [name.split() for name in names if name]

    if len(split) < 2:
        return ""

    prefix = []

    for words in zip(*split):

        if len(set(word.lower() for word in words)) != 1:
            break

        prefix.append(words[0])

    # Nunca se deja un nombre vacío.
    if any(len(words) <= len(prefix) for words in split):
        prefix = prefix[:-1]

    return " ".join(prefix)


def _strip_prefix(name, prefix):

    if prefix and name.lower().startswith(prefix.lower() + " "):
        return name[len(prefix) + 1:]

    return name


def _more(count, singular, plural):

    return f"y {count} {singular if count == 1 else plural} más"


def _join_words(words):

    words = list(dict.fromkeys(word for word in words if word))

    if not words:
        return ""

    if len(words) == 1:
        return words[0]

    return ", ".join(words[:-1]) + " y " + words[-1]


def _zip_text(uploaded, max_bytes=30_000_000):

    # Texto de los archivos de una app (zip) para buscar a qué
    # servicios llama. Si no se puede leer, devuelve "".
    try:

        if hasattr(uploaded, "seek"):
            uploaded.seek(0)

        source = (
            os.fspath(uploaded)
            if isinstance(uploaded, (str, os.PathLike))
            else uploaded
        )

        chunks = []

        total = 0

        with zipfile.ZipFile(source) as archive:

            for info in archive.infolist():

                if not info.filename.lower().endswith(
                    (".json", ".js", ".html", ".xml", ".sql", ".txt")
                ):
                    continue

                total += info.file_size

                if total > max_bytes:
                    break

                chunks.append(
                    archive.read(info).decode("utf-8", errors="ignore")
                )

        return "\n".join(chunks).lower()

    except Exception:

        return ""

    finally:

        if hasattr(uploaded, "seek"):

            try:
                uploaded.seek(0)
            except Exception:
                pass


def _app_targets(text, integration_names):

    # A qué sistemas llama una app VB/APEX, según lo que aparece
    # en sus archivos.
    targets = []

    if (
        "/ic/api/integration" in text
        or any(name.lower() in text for name in integration_names)
    ):
        targets.append("oic")

    if "/ords/" in text:
        targets.append("db")

    if "fscmrestapi" in text or "/fscmservice" in text:
        targets.append("erp")

    return targets


# =========================================================
# LATEST VERSIONS
# =========================================================
#
# Un .par puede traer varias versiones de la misma
# integración (01.00.0001, 01.00.0004...). Solo cuenta la
# versión más alta de cada una.
# =========================================================

def _version_key(version):

    return tuple(
        int(part) if part.isdigit() else 0
        for part in re.split(r"[.\-_]", version or "")
    )


def latest_integration_versions(package_path):

    latest = {}

    for iar in find_all_iar_files(package_path):

        try:

            extracted = extract_iar(iar)

            name = get_project_name(extracted)

            version = get_project_version(extracted)

        except Exception as error:

            print(f"[COMPONENTES] No se pudo leer {iar}: {error!r}")

            continue

        if not name:
            continue

        if (
            name not in latest
            or _version_key(version) > _version_key(latest[name][0])
        ):
            latest[name] = (version, extracted)

    return [
        (name, extracted)
        for name, (_version, extracted) in sorted(latest.items())
    ]


# =========================================================
# CALL ORDER
# =========================================================
#
# Orden en que una integración usa cada sistema por primera
# vez en su flujo principal (sin manejo de errores). Con él
# se ordenan los sistemas del diagrama de componentes y del
# de secuencia general.
# =========================================================

ERROR_BLOCK_PREFIXES = (
    "Si ocurre un error",
    "Manejo global de errores"
)


def _invokes_in_order(items):

    for current in items:

        if current["kind"] == "invoke":
            yield current.get("app") or {}

        if current["kind"] == "block" and current["text"].startswith(
            ERROR_BLOCK_PREFIXES
        ):
            continue

        yield from _invokes_in_order(current["children"])


def _category_order(extracted, applications):

    root = get_project_root(extracted)

    flows = get_endpoint_flows(
        root,
        build_application_map(applications)
    )

    order = []

    for flow in flows.values():

        if flow is None:
            continue

        for app in _invokes_in_order(
            analyze_flow(flow, applications, extracted, root)
        ):

            if app.get("IsIntegration"):
                continue

            key = classify_connection(
                app.get("ConnectionName") or app.get("Invoke") or "",
                app.get("Tipo")
            )

            if key not in order:
                order.append(key)

    return order


# =========================================================
# CONTRIBUTORS (aportadores al modelo común)
# =========================================================
#
# Cada insumo aporta elementos y relaciones al mismo modelo;
# el dibujo no depende de qué insumos hay. Estructura:
#
#   actors:       personas o disparadores (Usuario, Scheduler,
#                 Clientes REST)
#   apps:         aplicaciones del desarrollo (VB, APEX)
#   integrations: integraciones OIC del .par/.iar
#   systems:      sistemas por categoría (ERP, BD, FTP...)
#   relations:    {(origen, destino): verbos y protocolos}
#
# Una relación solo existe con evidencia en los archivos.
# =========================================================

# Orígenes de datos de BI Publisher que son del propio ERP
# Fusion: el reporte no sale del ERP, no es otra relación.
FUSION_DATASOURCE_PREFIXES = (
    "applicationdb",
    "oracle bi ee",
    "demo"
)

OIC_FLOW_PATTERN = re.compile(
    r"flows/rest/([A-Za-z0-9_]+)/"
)

ACTOR_COLOR = "#E8ECEF"

APP_COLOR = "#46607A"


def _new_model():

    return {
        "actors": {},
        "apps": {},
        "integrations": {},
        "internal_calls": set(),
        "called_integrations": set(),
        "systems": {},
        "relations": {},
        "ranks": {},
        "used_reports": set(),
        "used_tables": set(),
        "integration_names": []
    }


def _system(model, key):

    return model["systems"].setdefault(
        key,
        {"connections": {}, "extras": []}
    )


def _actor(model, key, title, technology, description):

    return model["actors"].setdefault(
        key,
        {
            "key": key,
            "title": title,
            "technology": technology,
            "description": description,
            "items": []
        }
    )


def _relate(model, src, dst, verb="", protocol=""):

    relation = model["relations"].setdefault(
        (src, dst),
        {"verbs": [], "protocols": []}
    )

    if verb and verb not in relation["verbs"]:
        relation["verbs"].append(verb)

    if protocol and protocol not in relation["protocols"]:
        relation["protocols"].append(protocol)


def _protocol(app, details):

    operation = details.get("operation", "")

    if operation.startswith("SFTP"):
        return "SFTP"

    kind = (app.get("Tipo") or "").upper()

    if kind == "DBAAS":
        return "SQL"

    return kind if kind and kind != "UNKNOWN" else ""


def contribute_oic(model, package_path):

    for name, extracted in latest_integration_versions(package_path):

        try:

            scheduled = bool(is_scheduled_integration(extracted))

            model["integrations"][name] = scheduled

            applications = read_project_xml(extracted)

            try:
                order = _category_order(extracted, applications)
            except Exception as error:
                print(f"[COMPONENTES] Sin orden de llamadas en {name}: {error!r}")
                order = []

            for position, key in enumerate(order):
                model["ranks"].setdefault(key, []).append(
                    position / max(1, len(order) - 1)
                )

            reports = report_names(extracted)

            for app in applications:

                connection = app.get("ConnectionName") or app.get("Invoke") or ""

                details = endpoint_details(extracted, app)

                if app.get("Role") == "source":
                    continue

                if app.get("IsIntegration"):

                    model["internal_calls"].add(
                        (name, app.get("IntegrationCode", ""))
                    )

                    continue

                key = classify_connection(connection, app.get("Tipo"))

                entry = _system(model, key)["connections"].setdefault(
                    connection,
                    {"operations": [], "integrations": set(), "reports": set(), "types": []}
                )

                entry["integrations"].add(name)

                protocol = _protocol(app, details)

                if protocol and protocol not in entry["types"]:
                    entry["types"].append(protocol)

                operation = details.get("operation", "")

                if operation and operation not in entry["operations"]:
                    entry["operations"].append(operation)

                # Reportes BIP: van con la conexión SOAP que los ejecuta.
                if details.get("operation") == "runReport":
                    entry["reports"].update(reports)
                    model["used_reports"].update(
                        report.lower() for report in reports
                    )

                if details.get("table"):
                    model["used_tables"].add(details["table"].upper())

                _relate(
                    model,
                    "oic",
                    key,
                    details.get("verb", "invoca"),
                    protocol
                )

        except Exception as error:

            print(f"[COMPONENTES] No se pudo leer {name}: {error!r}")

    model["integration_names"] = list(model["integrations"])

    scheduled_count = sum(1 for value in model["integrations"].values() if value)

    rest_count = len(model["integrations"]) - scheduled_count

    if scheduled_count:

        _actor(
            model,
            "scheduler",
            "Scheduler OIC",
            "Programación OIC",
            f"Ejecuta {scheduled_count} "
            f"{'integración programada' if scheduled_count == 1 else 'integraciones programadas'}"
        )

        _relate(model, "scheduler", "oic", "dispara por horario")

    if rest_count:

        _actor(
            model,
            "rest",
            "Clientes REST",
            "Sistemas consumidores",
            f"Invocan {rest_count} "
            f"{'integración REST' if rest_count == 1 else 'integraciones REST'}"
        )

        _relate(model, "rest", "oic", "invoca endpoints", "REST")


def _user(model):

    return _actor(
        model,
        "user",
        "Usuario de negocio",
        "Persona",
        "Usa las pantallas y reportes"
    )


def _open_zip(uploaded):

    if hasattr(uploaded, "seek"):
        uploaded.seek(0)

    source = (
        os.fspath(uploaded)
        if isinstance(uploaded, (str, os.PathLike))
        else uploaded
    )

    return zipfile.ZipFile(source)


VB_SERVICE_PATTERN = re.compile(
    # classic:    services/<conexión>/openapi3.json
    # VB Studio:  extension1/sources/services/self/<svc>/openapi3.json
    r"(?:^|/)services/(?:self/)?([^/]+)/openapi3\.json$"
)

VB_CATALOG_PATTERN = re.compile(
    r"(?:^|/)services/(?:self/)?catalog\.json$"
)

VB_BUSINESS_OBJECT_PATTERN = re.compile(
    r"(?:^|/)businessObjects/default/objects/([^/]+)/"
)

VB_CATALOG_URL_PATTERN = re.compile(
    # vb-catalog://backends/site_App:ics
    # vb-catalog://backends/base:fscmRest/11.13.18.05:{...}
    r"vb-catalog://backends/(?:[^:/]+:)?([^/]+)"
)


def _vb_server_text(spec, backend_types):

    # Servidores del servicio en minúsculas. En VB Studio el
    # servidor es una referencia vb-catalog:// al catálogo;
    # se agrega una pista del tipo de backend (ics = OIC,
    # fscmRest/hcmRest = Fusion) para que _call_target sepa
    # a qué sistema llama.
    texts = []

    for server in spec.get("servers") or []:

        url = server.get("url", "")

        texts.append(url)

        match = VB_CATALOG_URL_PATTERN.search(url)

        if not match:
            continue

        backend = match.group(1)

        backend_type = backend_types.get(backend, "")

        if backend.lower() == "ics" or backend_type == "ics":
            texts.append("/ic/api/integration")

        elif backend.lower() in ("fscmrest", "hcmrest", "crmrest"):
            texts.append("fscmrestapi")

    return " ".join(texts).lower()


def _vb_catalog(archive, names):

    # catalog.json de VB Studio: backends propios (ics,
    # custom...) y servicios de Fusion (fscmRest, hcmRest)
    # declarados sin openapi3.json propio.
    backend_types = {}

    catalog_services = []

    for name in names:

        if not VB_CATALOG_PATTERN.search(name):
            continue

        try:
            catalog = json.loads(archive.read(name).decode("utf-8", "ignore"))
        except ValueError:
            continue

        for backend, info in (catalog.get("backends") or {}).items():
            backend_types[backend] = (info or {}).get("serviceType", "")

        for service, spec in (catalog.get("services") or {}).items():
            catalog_services.append((service, spec or {}))

    return backend_types, catalog_services


def _vb_service_calls(connection, spec, server):

    calls = []

    for path, operations in (spec.get("paths") or {}).items():

        methods = [
            method.upper()
            for method in operations
            if method.lower() in ("get", "post", "put", "patch", "delete")
        ]

        if path == "/describe.openapi":

            # Servicio de Fusion del catálogo: los recursos que
            # usa la app vienen en x-vb.queryParameters.resources
            resources = (
                ((operations.get("get") or {}).get("x-vb") or {})
                .get("queryParameters", {})
                .get("resources", "")
            )

            for resource in filter(None, (r.strip() for r in resources.split(","))):
                calls.append({
                    "connection": connection,
                    "server": server,
                    "path": f"/{resource}",
                    "methods": ["GET"]
                })

            continue

        calls.append({
            "connection": connection,
            "server": server,
            "path": path,
            "methods": methods
        })

    return calls


def _analyze_vb_zip(uploaded):

    # Estructura de una app Visual Builder exportada.
    #
    # VB de OIC (classic):
    #   services/<conexión>/openapi3.json  servicios que llama
    #                                      (servidor + rutas)
    #   businessObjects/default/objects/   Business Objects
    #   webApps/<app>/pages/*-page.json     páginas
    #
    # VB Studio (App UI de Fusion):
    #   extension1/sources/services/self/catalog.json
    #   extension1/sources/services/self/<svc>/openapi3.json
    #   extension1/sources/ui/self/applications/<app>/flows/
    #       <flow>/pages/*-page.json
    result = {
        "calls": [],
        "business_objects": [],
        "pages": []
    }

    try:

        with _open_zip(uploaded) as archive:

            names = archive.namelist()

            backend_types, catalog_services = _vb_catalog(archive, names)

            for name in names:

                match = VB_SERVICE_PATTERN.search(name)

                if not match:
                    continue

                try:
                    spec = json.loads(archive.read(name).decode("utf-8", "ignore"))
                except ValueError:
                    continue

                result["calls"] += _vb_service_calls(
                    match.group(1),
                    spec,
                    _vb_server_text(spec, backend_types)
                )

            for service, spec in catalog_services:

                result["calls"] += _vb_service_calls(
                    service,
                    spec,
                    _vb_server_text(spec, backend_types)
                )

            result["business_objects"] = sorted({
                match.group(1)
                for match in (
                    VB_BUSINESS_OBJECT_PATTERN.search(name)
                    for name in names
                )
                if match
            })

            result["pages"] = sorted({
                re.sub(r"-page\.json$", "", name.split("/")[-1])
                for name in names
                if re.search(r"/pages/[^/]+-page\.json$", name)
                and not name.endswith("shell-page.json")
            })

    except Exception as error:

        print(f"[COMPONENTES] No se pudo leer la app: {error!r}")

    finally:

        if hasattr(uploaded, "seek"):

            try:
                uploaded.seek(0)
            except Exception:
                pass

    return result


def _call_target(call):

    # A qué sistema llama un servicio de la app, según su servidor.
    text = f"{call['server']} {call['path']}".lower()

    if "/ic/api/integration" in text or "integration.ocp.oraclecloud" in text:
        return "oic"

    if "fscmrestapi" in text or "/fscmservice" in text or "fa.ocs.oraclecloud" in text:
        return "erp"

    if "/ords/" in text:
        return "db"

    return "other"


def contribute_apps(model, kind, apps):

    for app in apps or []:

        label = _file_label(app)

        key = f"{kind.lower().replace(' ', '_')}:{label}"

        _user(model)

        _relate(model, "user", key, "usa la aplicación")

        if kind != "Visual Builder":

            # APEX: todavía sin análisis propio; se busca en el
            # texto de sus archivos a qué servicios llama.
            model["apps"][key] = {
                "key": key,
                "title": kind,
                "technology": "Aplicación web",
                "description": label,
                "items": []
            }

            for target in _app_targets(_zip_text(app), model["integration_names"]):

                if target != "oic":
                    _system(model, target)

                _relate(model, key, target, "invoca servicios", "REST")

            continue

        analysis = _analyze_vb_zip(app)

        items = []

        if analysis["pages"]:
            items.append(
                f"{len(analysis['pages'])} "
                f"{'página' if len(analysis['pages']) == 1 else 'páginas'}: "
                + ", ".join(analysis["pages"][:6])
                + (" ..." if len(analysis["pages"]) > 6 else "")
            )

        model["apps"][key] = {
            "key": key,
            "title": "Visual Builder",
            "technology": "Aplicación web",
            "description": label,
            "items": items
        }

        by_target = {}

        for call in analysis["calls"]:
            by_target.setdefault(_call_target(call), []).append(call)

        for target, calls in by_target.items():

            if target == "oic":

                # La ruta empieza con el código de la integración:
                # /ACME_CREAR_PEDIDO/1.0/start
                # En VB Studio la ruta es completa:
                # /ic/api/integration/v1/flows/rest/ACME/1.0/...
                codes = sorted({
                    (
                        OIC_FLOW_PATTERN.search(call["path"]).group(1)
                        if OIC_FLOW_PATTERN.search(call["path"])
                        else call["path"].strip("/").split("/")[0]
                    )
                    for call in calls
                    if call["path"].strip("/")
                })

                model["called_integrations"].update(codes)

                _relate(
                    model,
                    key,
                    "oic",
                    f"invoca {len(codes)} "
                    f"{'integración' if len(codes) == 1 else 'integraciones'}",
                    "REST"
                )

                continue

            _system(model, target)

            _relate(model, key, target, "invoca servicios", "REST")

        if analysis["business_objects"]:

            count = len(analysis["business_objects"])

            _system(model, "bo")["extras"].append((
                f"{label}: {count} "
                f"{'Business Object' if count == 1 else 'Business Objects'}",
                analysis["business_objects"][:6]
                + ([_more(count - 6, "objeto", "objetos")] if count > 6 else [])
            ))

            _relate(model, key, "bo", "lee y guarda datos", "REST")


def _bip_metadata(bip_files):

    # Reportes y data models de los archivos BIP (.xdoz, .xdmz,
    # .xdrz). Usa los mismos parsers que la sección 5 del DS140.
    from oic_doc_generator.backend.parsers.bip_archive_parser import (
        build_bip_artifact_tree,
        clean_bip_workspace
    )

    from oic_doc_generator.backend.parsers.bip_metadata_builder import (
        build_bip_metadata
    )

    tree = build_bip_artifact_tree(bip_files)

    try:
        return build_bip_metadata(tree)
    finally:
        try:
            clean_bip_workspace(tree.get("workspace"))
        except Exception:
            pass


def _report_folder(path, depth=2):

    # /Custom/Solucion/PE/AREA/Proceso/X.xdo
    #   -> "PE/AREA"
    parts = [part for part in (path or "").split("/") if part]

    if parts and parts[0].lower() == "custom":
        parts = parts[2:] if len(parts) > 3 else parts[1:]

    folder = parts[:-1][:depth]

    return "/".join(folder) or "Raíz del catálogo"


def contribute_bip(model, bip_files):

    if not bip_files:
        return

    try:
        metadata = _bip_metadata(bip_files)
    except Exception as error:
        print(f"[COMPONENTES] No se pudo leer BI Publisher: {error!r}")
        return

    reports = metadata.get("reports", [])

    if not reports:
        return

    folders = {}

    process_reports = set()

    external = set()

    executed = 0

    for report in reports:

        folder = _report_folder(report.get("report_path", ""))

        folders[folder] = folders.get(folder, 0) + 1

        if (report.get("report_name") or "").lower() in model["used_reports"]:
            executed += 1

        for dataset in report.get("dataset_sqls") or []:

            datasource = (dataset.get("datasource") or report.get("datasource") or "")

            if dataset.get("type") == "http":

                match = OIC_FLOW_PATTERN.search(dataset.get("url", ""))

                if match:

                    model["called_integrations"].add(match.group(1))

                    process_reports.add(report.get("report_name"))

                    _relate(model, "erp", "oic", "invoca integraciones", "REST")

                else:

                    _system(model, "other")

                    _relate(model, "erp", "other", "invoca servicios", "HTTP")

                continue

            if datasource and not datasource.lower().startswith(
                FUSION_DATASOURCE_PREFIXES
            ):
                external.add(datasource)

    lines = [
        f"{folder}: {count} {'reporte' if count == 1 else 'reportes'}"
        for folder, count in sorted(folders.items(), key=lambda item: -item[1])
    ]

    if len(lines) > 6:
        lines = lines[:6] + [_more(len(lines) - 6, "carpeta", "carpetas")]

    summary = f"{len(reports)} {'reporte' if len(reports) == 1 else 'reportes'}"

    if process_reports:
        summary += f" · {len(process_reports)} invocan OIC"

    if executed:
        summary += f" · {executed} ejecutados por OIC"

    _system(model, "erp")["extras"].append(
        (f"Reportes BI Publisher ({summary})", lines)
    )

    # Origen de datos propio (no del ERP): base de datos externa.
    for datasource in sorted(external):

        _system(model, "db")["extras"].append(
            (f"Origen de datos BIP {datasource}", [])
        )

        _relate(model, "erp", "db", "consulta datos", f"SQL · {datasource}")

    _user(model)

    _relate(model, "user", "erp", "ejecuta reportes")


def _normalize_name(text):

    # actualizarEstadoPedido / actualizar_estado_pedido /
    # ACTUALIZAR-ESTADO-PEDIDO -> "actualizarestadopedido"
    return re.sub(r"[^a-z0-9]", "", (text or "").lower())


def _ords_package_matches(model, database_metadata):

    # Cruce PROBABLE entre los servicios REST que OIC llama en la
    # base de datos (ORDS) y los procedimientos de los paquetes
    # del SQL: mismo nombre sin guiones ni mayúsculas.
    #   POST /actualizarEstadoPedido/{id}  <->
    #   XX_VENTAS_PKG.actualizar_estado_pedido
    members = {}

    for package in database_metadata.get("packages", []):

        for member in package.get("members") or []:

            name = member.get("name") if isinstance(member, dict) else str(member)

            if name:
                members[_normalize_name(name)] = (
                    package.get("package_name") or package.get("name") or "",
                    name
                )

    matches = {}

    db = model["systems"].get("db", {})

    for entry in db.get("connections", {}).values():

        for operation in entry["operations"]:

            for segment in operation.split():

                for part in segment.split("/"):

                    found = members.get(_normalize_name(part))

                    if found:
                        matches.setdefault(found[0], set()).add(found[1])

    return matches


def contribute_sql(model, database_metadata):

    if not database_metadata:
        return

    packages = sorted(set(filter(None, (
        package.get("package_name") or package.get("name")
        for package in database_metadata.get("packages", [])
    ))))

    tables = [
        (table.get("table_name") or table.get("name") or "").upper()
        for table in database_metadata.get("tables", [])
        if isinstance(table, dict)
    ]

    used = [table for table in tables if table in model["used_tables"]]

    lines = []

    if packages:
        lines.append(
            f"{len(packages)} {'paquete' if len(packages) == 1 else 'paquetes'}"
        )

    if tables:

        lines.append(
            f"{len(tables)} {'tabla' if len(tables) == 1 else 'tablas'}"
            + (f" ({len(used)} usadas por OIC)" if used else "")
        )

    for kind in ("views", "sequences", "triggers"):

        count = len(database_metadata.get(kind) or [])

        if count:
            lines.append(f"{count} " + {
                "views": "vistas" if count > 1 else "vista",
                "sequences": "secuencias" if count > 1 else "secuencia",
                "triggers": "triggers" if count > 1 else "trigger"
            }[kind])

    if lines:
        _system(model, "db")["extras"].append(
            ("Objetos SQL del desarrollo", lines)
        )

    # ORDS -> paquete: coincidencia probable por nombre.
    for package, procedures in sorted(
        _ords_package_matches(model, database_metadata).items()
    ):

        _system(model, "db")["extras"].append((
            f"Paquete {package} (expuesto por ORDS, por nombre)",
            sorted(procedures)
        ))


# =========================================================
# COLLECT
# =========================================================

def collect_development_components(
    package_path=None,
    visual_builder_apps=None,
    apex_apps=None,
    bip_files=None,
    database_metadata=None
):

    model = _new_model()

    if package_path:
        contribute_oic(model, package_path)

    contribute_apps(model, "Visual Builder", visual_builder_apps)

    contribute_apps(model, "APEX", apex_apps)

    contribute_bip(model, bip_files)

    contribute_sql(model, database_metadata)

    return _finish_model(model)


def _relation_label(relation):

    label = _join_words(relation["verbs"]).capitalize()

    if relation["protocols"]:
        label += f" [{', '.join(relation['protocols'])}]"

    return label


def _finish_model(model):

    prefix = _common_prefix_words(
        [
            connection
            for system in model["systems"].values()
            for connection in system["connections"]
        ]
        + list(model["integrations"])
    )

    elements = {}

    # -----------------------------------------------------
    # Actores y aplicaciones
    # -----------------------------------------------------

    for actor in model["actors"].values():

        elements[actor["key"]] = dict(
            actor,
            kind="actor",
            color=ACTOR_COLOR,
            dark_text=True,
            groups=[(actor["description"], actor["items"])]
        )

    for app in model["apps"].values():

        elements[app["key"]] = dict(
            app,
            kind="app",
            color=APP_COLOR,
            dark_text=False,
            groups=[(app["description"], app["items"])]
        )

    # -----------------------------------------------------
    # OIC: del desarrollo (.par) o solo invocado (BIP, VB)
    # -----------------------------------------------------

    has_oic = bool(model["integrations"])

    called = sorted(code for code in model["called_integrations"] if code)

    if has_oic or any(dst == "oic" for _src, dst in model["relations"]):

        groups = []

        if not has_oic and called:
            groups.append(("Integraciones invocadas", called))

        elements["oic"] = {
            "key": "oic",
            "kind": "oic",
            "title": "Oracle Integration Cloud",
            "technology": "Integraciones",
            "description": "",
            "color": OIC_COLOR,
            "dark_text": False,
            "groups": groups
        }

    # -----------------------------------------------------
    # Sistemas por categoría
    # -----------------------------------------------------

    ranks = model["ranks"]

    ordered = sorted(
        (category for category in CATEGORIES if category["key"] in model["systems"]),
        key=lambda category: (
            sum(ranks[category["key"]]) / len(ranks[category["key"]])
            if ranks.get(category["key"])
            else 2
        )
    )

    system_keys = []

    for category in ordered:

        system = model["systems"][category["key"]]

        connection_lines = []

        protocols = []

        for connection, entry in sorted(system["connections"].items()):

            count = len(entry["integrations"])

            for protocol in entry["types"]:
                if protocol not in protocols:
                    protocols.append(protocol)

            detail = " · ".join(
                part
                for part in (
                    "/".join(entry["types"]),
                    f"{count} {'integración' if count == 1 else 'integraciones'}",
                    (
                        f"{len(entry['reports'])} reportes BIP"
                        if len(entry["reports"]) > 1
                        else "1 reporte BIP" if entry["reports"] else ""
                    )
                )
                if part
            )

            connection_lines.append(
                f"{_strip_prefix(connection, prefix)} ({detail})"
            )

        groups = [(category["description"], [])]

        if connection_lines:
            groups.append(("Conexiones de OIC", connection_lines))

        groups.extend(system["extras"])

        elements[category["key"]] = {
            "key": category["key"],
            "kind": "system",
            "title": category["title"],
            "technology": " · ".join(protocols),
            "description": category["description"],
            "color": category["color"],
            "dark_text": False,
            "groups": groups,
            "connections": [
                _strip_prefix(connection, prefix)
                for connection in sorted(system["connections"])
            ]
        }

        system_keys.append(category["key"])

    # -----------------------------------------------------
    # Relaciones
    # -----------------------------------------------------

    relations = [
        {"src": src, "dst": dst, "label": _relation_label(relation)}
        for (src, dst), relation in model["relations"].items()
        if src in elements and dst in elements
    ]

    degree = {}

    for relation in relations:
        for key in (relation["src"], relation["dst"]):
            degree[key] = degree.get(key, 0) + 1

    for element in elements.values():
        element["linked"] = degree.get(element["key"], 0) > 0

    # -----------------------------------------------------
    # Centro del diagrama
    # -----------------------------------------------------
    #
    # OIC si el desarrollo tiene integraciones; si no, el
    # elemento con más relaciones (ERP con reportes, la app VB,
    # la base de datos...). Así el diagrama funciona con
    # cualquier combinación de insumos.
    # -----------------------------------------------------

    candidates = [
        key for key, element in elements.items()
        if element["kind"] != "actor"
    ]

    # Varias apps: el centro es el sistema al que más apps llaman
    # (p. ej. OIC), así cada app tiene su flecha hacia él.
    called_by_apps = {}

    for relation in relations:
        if relation["src"] in model["apps"] and relation["dst"] in elements:
            called_by_apps[relation["dst"]] = called_by_apps.get(relation["dst"], 0) + 1

    if has_oic:
        hub = "oic"
    elif len(model["apps"]) > 1 and called_by_apps:
        hub = max(called_by_apps, key=called_by_apps.get)
    elif candidates:
        priority = {"system": 0, "app": 1, "oic": 2}
        hub = max(
            candidates,
            key=lambda key: (
                degree.get(key, 0),
                -priority.get(elements[key]["kind"], 3)
            )
        )
    else:
        hub = None

    top = [
        key for key in list(model["actors"]) + list(model["apps"])
        if key != hub
    ]

    bottom = [
        key for key in (["oic"] if "oic" in elements else []) + system_keys
        if key != hub and key not in top
    ]

    return {
        "integrations": [
            {
                "name": name,
                "short": _strip_prefix(name, prefix),
                "scheduled": scheduled
            }
            for name, scheduled in sorted(model["integrations"].items())
        ],
        "internal_calls": len(model["internal_calls"]),
        "elements": elements,
        "hub": hub,
        "top": top,
        "bottom": bottom,
        "relations": relations
    }


def relation_label(model, src, dst):

    for relation in model.get("relations", []):

        if relation["src"] == src and relation["dst"] == dst:
            return relation["label"]

    return ""


# =========================================================
# DRAWING
# =========================================================
#
# Medidas en pulgadas, pensadas para el ancho útil del Word
# (5.7"): la imagen se inserta a tamaño real y la letra
# impresa queda en ~6.3 pt o más. Si el contenido es más alto
# que una página, Word la reduce para que quepa.
# =========================================================

PAGE_WIDTH = 5.7

DPI = 220

LINE_HEIGHT = 0.125

HEADER_HEIGHT = 0.4

PADDING = 0.06

FONT_TITLE = 10

FONT_BOX_TITLE = 8

FONT_SUBTITLE = 6.3

FONT_LINE = 6.3

FONT_ARROW = 6.2

CHAR_WIDTH = 0.62 / 72

# Con más integraciones, OIC muestra totales en vez de la lista.
MAX_LISTED_INTEGRATIONS = 20


def _chars_for(width, font_size):

    return max(8, int(width / (font_size * CHAR_WIDTH)))


def _split_long(word, width):

    # Rutas largas sin espacios (/valueSets/{id}/child/...) se
    # parten por "/" o "_" para que no se salgan de la caja.
    parts = []

    while len(word) > width:

        cut = max(word.rfind("/", 1, width), word.rfind("_", 1, width))

        if cut <= 0:
            cut = width

        parts.append(word[:cut])

        word = word[cut:]

    parts.append(word)

    return parts


def _wrap(text, width):

    words = [
        part
        for word in str(text).split()
        for part in _split_long(word, width)
    ]

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


def _group_lines(groups, width_chars):

    # [(titulo, [lineas])] -> [(texto, negrita, sangría)]
    lines = []

    for title, items in groups:

        for line in _wrap(title, width_chars):
            lines.append((line, True, 0))

        for item in items:

            for index, line in enumerate(_wrap(item, width_chars - 3)):
                lines.append((("• " if index == 0 else "  ") + line, False, 1))

    return lines


def _box_height(lines):

    return HEADER_HEIGHT + PADDING * 3 + max(1, len(lines)) * LINE_HEIGHT


def _draw_box(
    ax,
    x,
    y_top,
    width,
    title,
    subtitle,
    lines,
    color,
    dark_text=False,
    dashed=False
):

    height = _box_height(lines)

    ax.add_patch(
        FancyBboxPatch(
            (x, y_top - height),
            width,
            height,
            boxstyle="round,pad=0,rounding_size=0.05",
            linewidth=1.3,
            linestyle=(0, (4, 2)) if dashed else "solid",
            edgecolor=EDGE_DARK,
            facecolor=color,
            zorder=2
        )
    )

    text_color = "#1E1E1E" if dark_text else "white"

    # Título que siempre cabe en la caja (negrita: más ancha).
    title_size = min(
        FONT_BOX_TITLE,
        (width - 0.12) / (max(1, len(title)) * 0.7 / 72)
    )

    ax.text(
        x + width / 2,
        y_top - 0.13,
        title,
        ha="center",
        va="center",
        fontsize=title_size,
        fontweight="bold",
        color=text_color,
        zorder=3
    )

    if subtitle:

        ax.text(
            x + width / 2,
            y_top - 0.29,
            subtitle,
            ha="center",
            va="center",
            fontsize=FONT_SUBTITLE,
            fontstyle="italic",
            color=text_color,
            zorder=3
        )

    inner_top = y_top - HEADER_HEIGHT

    inner_height = height - HEADER_HEIGHT - PADDING

    ax.add_patch(
        FancyBboxPatch(
            (x + PADDING, inner_top - inner_height),
            width - PADDING * 2,
            inner_height,
            boxstyle="round,pad=0,rounding_size=0.03",
            linewidth=0.6,
            edgecolor="#9A9A9A",
            facecolor=INNER_COLOR,
            zorder=3
        )
    )

    first = inner_top - PADDING - LINE_HEIGHT / 2

    for index, (line, bold, indent) in enumerate(lines):

        ax.text(
            x + PADDING + 0.05 + indent * 0.06,
            first - index * LINE_HEIGHT,
            line,
            ha="left",
            va="center",
            fontsize=FONT_LINE,
            fontweight="bold" if bold else "normal",
            color="#222222",
            zorder=4
        )

    return height


def _arrow_with_label(ax, start, end, label, color, wrap_chars):

    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=8,
            linewidth=1.1,
            color=color,
            shrinkA=0,
            shrinkB=1,
            zorder=5
        )
    )

    if label:

        ax.text(
            (start[0] + end[0]) / 2,
            (start[1] + end[1]) / 2,
            "\n".join(_wrap(label, wrap_chars)),
            ha="center",
            va="center",
            fontsize=FONT_ARROW,
            color="#222222",
            linespacing=1.05,
            zorder=6,
            bbox={
                "boxstyle": "round,pad=0.12",
                "facecolor": "white",
                "edgecolor": color,
                "linewidth": 0.6
            }
        )


def _stack(heights, gap):

    return sum(heights) + gap * max(0, len(heights) - 1)


def render_component_diagram(
    model,
    title
):

    # Distribución vertical, pensada para la página del Word:
    #
    #   [ actores y apps (fila superior) ]
    #          │            │
    #   [ CENTRO: OIC, o el elemento con más relaciones ]
    #                       │ tronco
    #   [ Sistema A ] ──────┼────── [ Sistema B ]
    #
    # Las relaciones que no pasan por el centro (p. ej. Usuario
    # -> ERP cuando el centro es OIC) se anotan dentro de las
    # cajas, para no cruzar flechas por encima de otras cajas.

    if not model or not model.get("hub"):
        return None

    elements = model["elements"]

    hub = model["hub"]

    integrations = model["integrations"]

    margin = 0.04

    gap_y = 0.14

    gutter = 1.05

    title_space = 0.36

    relations = model["relations"]

    labels = {
        (relation["src"], relation["dst"]): relation["label"]
        for relation in relations
    }

    # Relaciones que no tocan el centro: notas en las cajas.
    notes = {key: [] for key in elements}

    for relation in relations:

        if hub in (relation["src"], relation["dst"]):
            continue

        src = elements[relation["src"]]

        dst = elements[relation["dst"]]

        notes[relation["dst"]].append(
            f"◄ {src['title']}: {relation['label'].lower()}"
        )

        notes[relation["src"]].append(
            f"► {dst['title']}: {relation['label'].lower()}"
        )

    def element_lines(key, chars):

        element = elements[key]

        lines = []

        for title_text, items in element["groups"]:

            if not items and key != hub and element["kind"] == "system":
                # Descripción de la categoría: texto normal.
                lines.extend((line, False, 0) for line in _wrap(title_text, chars))
                continue

            lines.extend(_group_lines([(title_text, items)], chars))

        for note in notes.get(key, []):
            lines.extend((line, False, 0) for line in _wrap(note, chars))

        if not element["linked"]:
            lines.append(("sin relación detectada", False, 0))

        return lines or [("", False, 0)]

    # -----------------------------------------------------
    # TOP (actores y apps)
    # -----------------------------------------------------

    top = model["top"]

    per_row = min(4, max(1, len(top)))

    source_gap = 0.25

    source_width = (
        (PAGE_WIDTH - 2 * margin - source_gap * (per_row - 1)) / per_row
    )

    source_chars = _chars_for(source_width - 0.2, FONT_LINE)

    top_lines = {key: element_lines(key, source_chars) for key in top}

    top_rows = [
        top[index:index + per_row]
        for index in range(0, len(top), per_row)
    ]

    top_row_heights = [
        max(_box_height(top_lines[key]) for key in row)
        for row in top_rows
    ]

    arrow_space = 0.5 if top else 0

    # -----------------------------------------------------
    # HUB (centro, a lo ancho)
    # -----------------------------------------------------

    hub_width = PAGE_WIDTH - 2 * margin

    hub_columns = 3 if hub == "oic" and integrations else 2

    column_width = (hub_width - 2 * PADDING - 0.1) / hub_columns

    column_chars = _chars_for(column_width - 0.12, FONT_LINE)

    if hub == "oic" and integrations:

        scheduled = sum(1 for integration in integrations if integration["scheduled"])

        if len(integrations) > MAX_LISTED_INTEGRATIONS:

            # Muchas integraciones: totales (el detalle está en 2.5).
            hub_items = [
                f"{scheduled} programadas",
                f"{len(integrations) - scheduled} REST",
                "detalle de cada una en la sección 2.5"
            ]

        else:

            hub_items = [
                integration["short"] + (" (prog.)" if integration["scheduled"] else "")
                for integration in integrations
            ]

        hub_header = f"{len(integrations)} integraciones"

        if model["internal_calls"]:
            hub_header += f" · {model['internal_calls']} llamadas entre integraciones"

        cells = [
            [
                ("• " if index == 0 else "  ") + line
                for index, line in enumerate(_wrap(item, column_chars - 2))
            ]
            for item in hub_items
        ]

    else:

        hub_header = ""

        # Un bloque por grupo, repartidos en dos columnas.
        cells = []

        for title_text, items in elements[hub]["groups"]:

            lines = [
                text for text, _bold, _indent
                in _group_lines([(title_text, items)], column_chars)
            ]

            # El título va con su primer elemento; el resto, una
            # celda por línea para repartirse en las columnas.
            cells.append(lines[:2])

            cells.extend([line] for line in lines[2:])

        for note in notes.get(hub, []):
            cells.append(_wrap(note, column_chars))

    columns = [[] for _ in range(hub_columns)]

    per_column = -(-sum(len(cell) for cell in cells) // hub_columns)

    current = 0

    for cell in cells:

        if columns[current] and len(columns[current]) + len(cell) > per_column and current < hub_columns - 1:
            current += 1

        columns[current].extend(cell)

    hub_rows = max(len(column) for column in columns)

    hub_height = (
        HEADER_HEIGHT + PADDING * 3
        + (hub_rows + (1 if hub_header else 0)) * LINE_HEIGHT
    )

    # -----------------------------------------------------
    # BOTTOM (sistemas a los lados del tronco)
    # -----------------------------------------------------

    bottom = model["bottom"]

    system_width = (PAGE_WIDTH - 2 * margin - gutter) / 2

    system_chars = _chars_for(system_width - 0.2, FONT_LINE)

    bottom_lines = {key: element_lines(key, system_chars) for key in bottom}

    column_tops = [0.0, 0.35]

    placed = [[], []]

    for key in bottom:

        side = 0 if column_tops[0] <= column_tops[1] else 1

        placed[side].append((key, column_tops[side]))

        column_tops[side] += _box_height(bottom_lines[key]) + gap_y

    bottom_height = (
        max(column_tops[side] for side in (0, 1) if placed[side]) - gap_y
        if bottom
        else 0
    )

    # -----------------------------------------------------
    # FIGURE
    # -----------------------------------------------------

    total_height = (
        title_space
        + sum(top_row_heights)
        + gap_y * max(0, len(top_rows) - 1)
        + arrow_space
        + hub_height
        + (0.45 if bottom else 0)
        + bottom_height
        + 0.08
    )

    figure = plt.figure(
        figsize=(PAGE_WIDTH, total_height),
        dpi=DPI
    )

    ax = figure.add_axes([0, 0, 1, 1])

    ax.set_xlim(0, PAGE_WIDTH)

    ax.set_ylim(0, total_height)

    ax.axis("off")

    ax.text(
        PAGE_WIDTH / 2,
        total_height - title_space / 2,
        title,
        ha="center",
        va="center",
        fontsize=FONT_TITLE,
        fontweight="bold",
        color="#111111"
    )

    y = total_height - title_space

    # -----------------------------------------------------
    # DRAW TOP
    # -----------------------------------------------------

    anchors = {}

    for row, row_height in zip(top_rows, top_row_heights):

        row_width = len(row) * source_width + (len(row) - 1) * source_gap

        x = (PAGE_WIDTH - row_width) / 2

        for key in row:

            element = elements[key]

            _draw_box(
                ax,
                x,
                y,
                source_width,
                element["title"],
                element["technology"],
                top_lines[key],
                element["color"],
                dark_text=element.get("dark_text", False),
                dashed=not element["linked"]
            )

            anchors[key] = (
                x + source_width / 2,
                y - _box_height(top_lines[key])
            )

            x += source_width + source_gap

        y -= row_height + gap_y

    if top_rows:
        y += gap_y

    hub_top = y - arrow_space

    for key, (x, box_bottom) in anchors.items():

        label = labels.get((key, hub))

        if not label:
            continue

        _arrow_with_label(
            ax,
            (x, box_bottom),
            (x, hub_top),
            label,
            EDGE_DARK,
            _chars_for(source_width * 0.8, FONT_ARROW)
        )

    # -----------------------------------------------------
    # DRAW HUB
    # -----------------------------------------------------

    hub_element = elements[hub]

    _draw_box(
        ax,
        margin,
        hub_top,
        hub_width,
        hub_element["title"],
        hub_element["technology"],
        ([(hub_header, True, 0)] if hub_header else [])
        + [("", False, 0)] * hub_rows,
        hub_element["color"],
        dark_text=hub_element.get("dark_text", False),
        dashed=not hub_element["linked"] and bool(bottom or top)
    )

    first = (
        hub_top - HEADER_HEIGHT - PADDING - LINE_HEIGHT / 2
        - (LINE_HEIGHT if hub_header else 0)
    )

    for column_index, column in enumerate(columns):

        x = margin + PADDING + 0.05 + column_index * column_width

        for row_index, line in enumerate(column):

            bold = (
                hub != "oic"
                and not line.startswith(("•", " "))
            )

            ax.text(
                x,
                first - row_index * LINE_HEIGHT,
                line,
                ha="left",
                va="center",
                fontsize=FONT_LINE,
                fontweight="bold" if bold else "normal",
                color="#222222",
                zorder=4
            )

    # -----------------------------------------------------
    # DRAW BOTTOM + TRONCO
    # -----------------------------------------------------

    if not bottom:
        return _save_figure(figure, "componentes.png")

    bottom_top = hub_top - hub_height - 0.45

    trunk_x = PAGE_WIDTH / 2

    branch_ys = []

    # Etiquetas del tronco: se dibujan al final, de arriba hacia
    # abajo, sin superponerse.
    pending_labels = []

    for side, items in enumerate(placed):

        x = margin if side == 0 else PAGE_WIDTH - margin - system_width

        for key, offset in items:

            element = elements[key]

            box_top = bottom_top - offset

            _draw_box(
                ax,
                x,
                box_top,
                system_width,
                element["title"],
                element["technology"],
                bottom_lines[key],
                element["color"],
                dark_text=element.get("dark_text", False),
                dashed=not element["linked"]
            )

            forward = labels.get((hub, key))

            backward = labels.get((key, hub))

            if not forward and not backward:
                continue

            branch_y = box_top - 0.22

            branch_ys.append(branch_y)

            edge_x = x + system_width if side == 0 else x

            # Flecha hacia el sistema, hacia el centro o ambas.
            style = (
                "<|-|>" if forward and backward
                else "-|>" if forward
                else "<|-"
            )

            ax.add_patch(
                FancyArrowPatch(
                    (trunk_x, branch_y),
                    (edge_x, branch_y),
                    arrowstyle=style,
                    mutation_scale=8,
                    linewidth=1.1,
                    color=element["color"],
                    shrinkA=0,
                    shrinkB=1,
                    zorder=5
                )
            )

            label_text = "\n".join(
                part for part in (
                    forward,
                    f"↩ {backward}" if backward and forward else backward
                )
                if part
            )

            label_lines = []

            for part in label_text.split("\n"):
                label_lines.extend(
                    _wrap(part, _chars_for(gutter - 0.16, FONT_ARROW))
                )

            pending_labels.append(
                (branch_y, label_lines, element["color"])
            )

    line_height = FONT_ARROW * 1.15 / 72

    previous_bottom = None

    for branch_y, label_lines, color in sorted(
        pending_labels,
        key=lambda item: -item[0]
    ):

        # Debajo de su rama; más abajo si choca con la anterior.
        label_top = branch_y - 0.05

        if previous_bottom is not None:
            label_top = min(label_top, previous_bottom - 0.06)

        ax.text(
            trunk_x,
            label_top,
            "\n".join(label_lines),
            ha="center",
            va="top",
            fontsize=FONT_ARROW,
            color="#222222",
            linespacing=1.05,
            zorder=6,
            bbox={
                "boxstyle": "round,pad=0.1",
                "facecolor": "white",
                "edgecolor": color,
                "linewidth": 0.6
            }
        )

        previous_bottom = label_top - len(label_lines) * line_height - 0.04

    if branch_ys:

        ax.plot(
            [trunk_x, trunk_x],
            [hub_top - hub_height, min(branch_ys)],
            color=EDGE_DARK,
            linewidth=1.3,
            zorder=4
        )

    return _save_figure(figure, "componentes.png")


def _save_figure(figure, name):

    png_file = os.path.join(
        tempfile.mkdtemp(),
        name
    )

    figure.savefig(
        png_file,
        dpi=DPI,
        facecolor="white"
    )

    plt.close(figure)

    return png_file


def generate_component_diagram(
    title,
    package_path=None,
    visual_builder_apps=None,
    apex_apps=None,
    bip_files=None,
    database_metadata=None
):

    return render_component_diagram(
        collect_development_components(
            package_path=package_path,
            visual_builder_apps=visual_builder_apps,
            apex_apps=apex_apps,
            bip_files=bip_files,
            database_metadata=database_metadata
        ),
        title
    )
