# =========================================================
# FILE:
# oic_doc_generator/backend/generators/vbs_installation_section.py
# =========================================================
#
# IM090 - 3.4 Instalación de la aplicación de Visual Builder
# Studio (App UI / extensión de Oracle Fusion).
#
# Va después de BD (3.1), BI Publisher (3.2) y OIC (3.3): la
# aplicación consume las integraciones ya instaladas.
#
# Flujo: la extensión ya está en el repositorio del proyecto
# de VB Studio del ambiente origen (p. ej. TEST) y se despliega
# al destino (p. ej. PROD) con el job de despliegue. El zip
# exportado NO se importa: solo da la metadata (páginas,
# backends, servicios). Por cada backend se matricula la
# configuración en el ERP destino (trap-admin) según la
# autenticación elegida en el diálogo del IM090.
# =========================================================

import re

from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.shared import Pt, RGBColor

from oic_doc_generator.backend.parsers.vbs_backend_parser import (
    AUTH_BY_KEY
)

from oic_doc_generator.backend.utils.word_utils import (
    apply_table_header_style,
    create_header
)


SECTION_NUMBER = "3.4"

TOKEN_URL = (
    "https://<dominio de identidad>.identity.oraclecloud.com"
    "/oauth2/v1/token"
)

# Nombre del método en la lista Authentication de
# "Manage Backends for Visual Builder Studio" (ERP).
ERP_AUTH_LABEL = {
    "oauth2_client_credentials": "OAuth2.0 Client Credentials",
    "oauth2_resource_owner": "OAuth2.0 Resource Owner Password Credentials",
    "oauth2_code_grant": "OAuth2.0 Authorization Code",
    "oauth2_user_assertion": "OAuth2.0 User Assertion",
}

# Métodos que necesitan una aplicación confidencial en el
# dominio de identidad, con sus grant types.
CONFIDENTIAL_GRANTS = {
    "oauth2_client_credentials": "Client Credentials y Refresh Token",
    "oauth2_resource_owner": "Resource Owner y Refresh Token",
    "oauth2_code_grant": "Authorization Code y Refresh Token",
}

AUTH_NOTES = {
    "oauth2_client_credentials":
        "Todas las llamadas usan la identidad de la aplicación OAuth2, "
        "no la del usuario que inició sesión.",
    "oauth2_resource_owner":
        "Use un usuario técnico (de servicio), no un usuario personal: "
        "su contraseña queda registrada en el backend.",
    "oauth2_code_grant":
        "El usuario final debe autorizar el acceso la primera vez que "
        "la aplicación llama al servicio. Registre en la aplicación "
        "OAuth2 la URL de retorno que indique la página de backends.",
    "basic":
        "Oracle recomienda OAuth 2.0 en lugar de Basic Authentication "
        "en ambientes productivos. Use un usuario técnico.",
    "oauth2_user_assertion":
        "Se propaga la identidad del usuario que inició sesión: debe "
        "existir en el servicio con los permisos necesarios, y el "
        "servicio debe estar en el mismo dominio de identidad que el "
        "ERP y permitir CORS para el dominio del ERP.",
    "oracle_cloud_account":
        "No requiere credenciales: se usa la cuenta del usuario que "
        "inició sesión en ERP Cloud. El servicio debe estar en el mismo "
        "dominio de identidad que el ERP.",
    "oci_signature":
        "Según Oracle, un backend con OCI Signature usado en una App UI "
        "falla con error 500 en la vista previa y después del "
        "despliegue. Valide este método antes del pase.",
    "none":
        "El servicio se llama sin autenticación: cualquier usuario de "
        "la aplicación puede acceder a él.",
}

SERVER_KIND_LABEL = {
    "local": "Servidor local",
    "in_source": "Servidor en el código fuente",
    "reference": "Referencia a otro backend"
}


# =========================================================
# HELPERS
# =========================================================

def _helpers():

    # Import diferido: installation_manual_generator importa
    # este módulo.
    from oic_doc_generator.backend.generators.installation_manual_generator import (
        add_im090_bullet,
        add_information_box
    )

    return add_im090_bullet, add_information_box


def _text(document, text, bold=False, size=10, space_before=4, color=None):

    paragraph = document.add_paragraph()

    paragraph.paragraph_format.space_before = Pt(space_before)
    paragraph.paragraph_format.space_after = Pt(2)

    run = paragraph.add_run(text)

    run.bold = bold
    run.font.name = "Arial"
    run.font.size = Pt(size)

    if color:
        run.font.color.rgb = color

    return paragraph


def _step(document, text):

    return _text(document, text, bold=True, space_before=8)


def _table(document, headers, rows, title=None):

    table = document.add_table(rows=0, cols=len(headers))

    table.style = "Table Grid"

    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    if title:

        cells = table.add_row().cells

        merged = cells[0].merge(cells[-1]) if len(cells) > 1 else cells[0]

        merged.text = title

        apply_table_header_style(merged, fill="BFBFBF")

    cells = table.add_row().cells

    for index, header in enumerate(headers):

        cells[index].text = header

        apply_table_header_style(cells[index])

    for values in rows:

        cells = table.add_row().cells

        for index, value in enumerate(values):

            cells[index].text = str(
                value if value not in (None, "") else "-"
            )

            for paragraph in cells[index].paragraphs:
                for run in paragraph.runs:
                    run.font.name = "Arial"
                    run.font.size = Pt(8)

    document.add_paragraph("")

    return table


def _important(info_box, document, text):

    info_box(document, "Importante", text)

    document.add_paragraph("")


def _auth_label(key):

    method = AUTH_BY_KEY.get(key)

    return method["label"] if method else "Por definir"


def _erp_auth_label(key):

    return ERP_AUTH_LABEL.get(key) or _auth_label(key)


def _slug(text):

    return re.sub(r"[^A-Za-z0-9]+", "_", text or "").strip("_").upper()


def _settings(plan):

    settings = dict(plan.get("settings") or {})

    settings["source"] = (settings.get("source_env") or "").strip() or "TEST"

    settings["target"] = (settings.get("target_env") or "").strip() or "PROD"

    settings["erp"] = (
        (settings.get("target_erp_url") or "").strip().rstrip("/")
        or f"<URL ERP {settings['target']}>"
    )

    settings["oic"] = (
        (settings.get("target_oic_url") or "").strip().rstrip("/")
        or f"<URL OIC {settings['target']}>"
    )

    return settings


def _repository(app, settings):

    configured = (settings.get("repository") or "").strip()

    if configured:
        return configured

    applications = app.get("applications") or []

    if applications:
        return re.sub(r"\s+", "_", applications[0]["name"].strip())

    return "<repositorio>"


def _is_oic(backend):

    return backend.get("service_type") == "ics" or backend["id"] == "ics"


def _instance_url(backend, settings):

    if _is_oic(backend):
        return settings["oic"]

    return f"<URL del servicio {backend['label']} en {settings['target']}>"


def _registrable(backend):

    # Se matriculan en el ERP destino los backends sin servidor
    # en el código fuente que usa algún servicio o a los que se
    # les eligió un método de autenticación.
    if backend["server_kind"] == "in_source":
        return False

    return bool(backend.get("services") or backend.get("auth"))


def _oauth_app_name(app, backend, settings):

    return (
        f"OAUTH2_{_slug(backend['id'])}_"
        f"{_slug(app.get('extension_name'))}_{_slug(settings['target'])}"
    )


# =========================================================
# METADATA Y AMBIENTES
# =========================================================

def _add_metadata(document, app, bullet, info_box):

    _step(document, "Metadata de la aplicación")

    applications = app.get("applications") or []

    _table(
        document,
        ["Nombre", "ID de extensión", "Versión", "Aplicación (App UI)"],
        [
            (
                app.get("extension_name"),
                app.get("extension_id"),
                app.get("extension_version"),
                ", ".join(item["id"] for item in applications)
            )
        ],
        title="Extensión"
    )

    pages = [
        page
        for item in applications
        for page in item.get("pages") or []
    ]

    _text(document, f"Páginas: {len(pages)}", bold=True)

    for page in pages:
        bullet(document, page)

    backends = [
        backend for backend in app["backends"]
        if backend.get("services") or backend.get("auth")
    ]

    _text(document, f"Backends: {len(backends)}", bold=True)

    for backend in backends:

        services = len(backend.get("services") or [])

        bullet(
            document,
            f"{backend['label']} ({backend['id']}): {services} "
            f"{'servicio' if services == 1 else 'servicios'}, "
            f"autenticación {_auth_label(backend.get('auth'))}."
        )

    services = sorted({
        service
        for backend in app["backends"]
        for service in backend.get("services") or []
    })

    _text(document, f"Servicios: {len(services)}", bold=True)

    for service in services:
        bullet(document, service)

    erp_services = app.get("erp_services") or []

    _text(document, f"Servicios de ERP Cloud: {len(erp_services)}", bold=True)

    for service in erp_services or ["No aplica."]:
        bullet(document, service)

    if erp_services:
        _text(
            document,
            "Los servicios de ERP Cloud usan la sesión del usuario en el "
            "ERP y no requieren configuración.",
            size=9
        )

    _text(
        document,
        f"Archivo de referencia: ../VBS/{app['file_name']} (solo como "
        "referencia de la metadata; no se importa en el ambiente).",
        size=9,
        space_before=8
    )

    for warning in app.get("warnings") or []:

        info_box(document, "Advertencia", warning, fill="FCE4D6")

        document.add_paragraph("")


def _add_environments(document, settings):

    _step(document, "Ambientes de la aplicación")

    _text(
        document,
        "La aplicación se mantiene en el proyecto de Visual Builder "
        f"Studio asociado al ambiente {settings['source']} y desde allí se "
        f"despliega al ambiente {settings['target']} mediante el job de "
        "despliegue del proyecto. No se importa ningún archivo: el "
        "repositorio del proyecto es el origen del despliegue."
    )

    _table(
        document,
        ["Ambiente", "Función", "ERP Cloud", "Oracle Integration Cloud"],
        [
            (
                settings["source"],
                "Origen. Proyecto, repositorio y jobs de VB Studio; "
                "aplicación certificada.",
                f"<URL ERP {settings['source']}>",
                f"<URL OIC {settings['source']}>"
            ),
            (
                settings["target"],
                "Destino del despliegue.",
                settings["erp"],
                settings["oic"]
            )
        ],
        title="Ambientes"
    )


# =========================================================
# ACCESO Y AMBIENTES
# =========================================================

def _add_access(document, number, settings, bullet):

    create_header(
        document,
        f"{number}\tAcceso a Visual Builder Studio y validación de los "
        "ambientes",
        size=11
    )

    _step(document, "1. Acceso al proyecto")

    _text(
        document,
        "Acceda a Oracle Visual Builder Studio con un usuario que tenga el "
        "rol de propietario (Owner) del proyecto e ingrese al proyecto de "
        f"la aplicación en el ambiente {settings['source']}."
    )

    _step(document, "2. Validación de los ambientes del proyecto")

    _text(
        document,
        "En el menú lateral, seleccione Environments y verifique que "
        f"existan los ambientes {settings['source']} y "
        f"{settings['target']}, cada uno con una instancia de tipo "
        "Oracle Cloud Applications en estado activo (indicador en verde)."
    )

    _text(
        document,
        f"Si el ambiente {settings['target']} no existe, regístrelo desde "
        "la página Manage Extension Lifecycle:"
    )

    bullet(
        document,
        "En Environments, haga clic en Extension Lifecycle y luego en "
        "Add Environment."
    )

    bullet(
        document,
        f"En Base URL ingrese la URL del ERP {settings['target']} "
        f"({settings['erp']}) y en Environment Name el nombre del ambiente."
    )

    bullet(
        document,
        "En Username y Password ingrese las credenciales de un usuario "
        f"del ERP {settings['target']} y haga clic en Add. Inicie sesión "
        "en la instancia agregada e ingrese las credenciales que se usarán "
        "para la página Manage Extension Lifecycle."
    )

    bullet(
        document,
        "Verifique que el ambiente figure en la lista con el indicador "
        "en verde."
    )


# =========================================================
# REPOSITORIO Y BACKENDS EN VBS
# =========================================================

def _add_repository(document, number, app, settings, registration_number,
                    bullet, info_box):

    repository = _repository(app, settings)

    create_header(
        document,
        f"{number}\tVerificación del repositorio y de los backends en "
        "Visual Builder Studio",
        size=11
    )

    _step(document, "1. Repositorio de la aplicación")

    bullet(
        document,
        f"Seleccione Git y verifique que el repositorio {repository} "
        "contenga en la rama main la versión certificada de la "
        "aplicación (carpeta extension1/sources, extensión "
        f"{app.get('extension_id') or '<ID de extensión>'})."
    )

    bullet(
        document,
        "Seleccione Builds y verifique que existan los jobs de "
        "empaquetado (Package) y despliegue (Deploy) del repositorio."
    )

    if not any(_registrable(b) for b in app["backends"]):
        return

    _step(document, "2. Backends de la aplicación")

    _text(
        document,
        "Abra un workspace del repositorio, seleccione el panel Services y "
        "la pestaña Backends, y verifique cada backend:"
    )

    _table(
        document,
        ["Backend", "ID", "Servidor", "Autenticación", "Servicios"],
        [
            (
                backend["label"],
                backend["id"],
                SERVER_KIND_LABEL.get(
                    backend["server_kind"], backend["server_kind"]
                ),
                (
                    "No aplica"
                    if backend["server_kind"] == "reference"
                    and not backend.get("auth")
                    else _auth_label(backend.get("auth"))
                ),
                len(backend.get("services") or [])
            )
            for backend in app["backends"]
        ],
        title="Backends"
    )

    _text(
        document,
        "Los servidores deben figurar como Local server definition: la URL "
        "y las credenciales no forman parte del código fuente. En el "
        f"ambiente {settings['target']} el backend toma la configuración "
        f"matriculada en su ERP (sección {registration_number}), por lo "
        "que al desplegar no se modifica la configuración del backend en "
        "Visual Builder Studio."
    )

    _important(
        info_box,
        document,
        "No utilice la opción In-Source Server: guardaría la URL del "
        f"ambiente {settings['source']} en el código fuente y la "
        f"aplicación desplegada en {settings['target']} invocaría a ese "
        "ambiente. La opción Edit Configuration de la pestaña Servers abre "
        f"la página del ERP {settings['source']}; no la use para "
        f"matricular el backend en {settings['target']}."
    )

    for backend in app["backends"]:

        if backend["server_kind"] == "in_source":

            _important(
                info_box,
                document,
                f"El backend {backend['label']} tiene un servidor en el "
                f"código fuente ({backend.get('in_source_url') or '-'}): "
                f"verifique que la URL corresponda a {settings['target']} "
                "antes de desplegar."
            )


# =========================================================
# MATRICULACIÓN EN EL ERP DESTINO
# =========================================================

def _add_identity_steps(document, app, backend, settings, bullet, info_box):

    auth = backend.get("auth")

    target = settings["target"]

    oauth_app = _oauth_app_name(app, backend, settings)

    resource = (
        f"la instancia de OIC {target} ({settings['oic']})"
        if _is_oic(backend)
        else f"el servicio {backend['label']} de {target}"
    )

    _step(
        document,
        f"1. Aplicación OAuth2 en el dominio de identidad de {target}"
    )

    if auth in CONFIDENTIAL_GRANTS:

        bullet(
            document,
            "Acceda a la consola de Oracle Cloud Infrastructure (OCI), "
            "navegue a Identity & Security > Domains y seleccione el "
            f"dominio de identidad utilizado por {resource}."
        )

        bullet(
            document,
            "Seleccione Integrated applications, haga clic en Add "
            "application, elija Confidential Application y haga clic en "
            "Launch workflow. Asigne el nombre y la descripción:"
        )

        _table(
            document,
            ["Campo", "Valor"],
            [
                ("Name", oauth_app),
                ("Description",
                 f"OAuth2 para el backend {backend['id']} de "
                 f"{app.get('extension_name') or 'la aplicación'} "
                 f"({target})")
            ],
            title=f"Valores del ambiente {target}"
        )

        bullet(
            document,
            "Seleccione Configure OAuth y marque Client configuration. En "
            "Authorization seleccione los grant types "
            f"{CONFIDENTIAL_GRANTS[auth]}."
        )

        bullet(
            document,
            "En Client type seleccione Confidential. En Token issuance "
            "policy > Authorized resources seleccione Specific, habilite "
            f"Add resources y con Add Scope agregue el recurso de "
            f"{resource}."
        )

        bullet(
            document,
            "Guarde la aplicación y actívela con Actions > Activate. En "
            "General Information registre el Client ID, el Client Secret "
            "(Show secret) y el Scope."
        )

        if _is_oic(backend):

            bullet(
                document,
                f"En Oracle Cloud Services ubique la instancia de OIC "
                f"{target}, seleccione Application Roles, en el rol "
                "ServiceInvoker elija Manage applications y, en Assigned "
                f"applications, agregue la aplicación {oauth_app}."
            )

        _important(
            info_box,
            document,
            "Mantenga el Client Secret en un lugar seguro: no lo incluya "
            "en este documento ni en el repositorio."
        )

    elif auth == "oauth2_user_assertion":

        bullet(
            document,
            f"Verifique que {resource} esté registrado como recurso en el "
            "dominio de identidad del ERP y registre su scope."
        )

        bullet(
            document,
            "Agregue ese scope a la aplicación OAuth de Oracle Cloud "
            "Applications en el dominio de identidad."
        )

    elif auth == "oci_signature":

        bullet(
            document,
            "En la consola de OCI, genere (o reutilice) una API key para "
            "el usuario técnico y registre Tenancy OCID, User OCID y "
            "Fingerprint."
        )


def _registration_rows(app, backend, settings):

    auth = backend.get("auth")

    target = settings["target"]

    oauth_app = _oauth_app_name(app, backend, settings)

    extension_id = (
        backend.get("reference_namespace")
        if backend["server_kind"] == "reference"
        else None
    ) or app.get("extension_id") or "<ID de extensión>"

    rows = [
        ("Extension ID / Backend Name", f"{extension_id} / {backend['id']}"),
        ("Instance URL", _instance_url(backend, settings)),
        ("Authentication", _erp_auth_label(auth) if auth else "<Por definir>"),
        ("Backend Description", f"backend {target}"),
    ]

    if auth in CONFIDENTIAL_GRANTS:

        rows += [
            ("Client ID", f"Client ID de {oauth_app}"),
            ("Secret", f"Client Secret de {oauth_app}"),
            ("Scope", f"Scope de {oauth_app}"),
        ]

        if auth == "oauth2_code_grant":
            rows.append((
                "Authorization URL",
                "https://<dominio de identidad>.identity.oraclecloud.com"
                "/oauth2/v1/authorize"
            ))

        rows.append(("Token URL", TOKEN_URL))

        if auth == "oauth2_resource_owner":
            rows += [
                ("Username", "Usuario técnico con acceso al servicio"),
                ("Password", "Contraseña del usuario técnico"),
            ]

        rows.append((
            "Add credentials to payload rather than header",
            "Sin marcar"
        ))

    elif auth == "basic":

        rows += [
            ("Username", "Usuario técnico con acceso al servicio"),
            ("Password", "Contraseña del usuario técnico"),
        ]

    elif auth == "oauth2_user_assertion":

        rows.append(("Scope", "Scope del recurso registrado"))

    elif auth == "oci_signature":

        rows += [
            ("Tenancy OCID", "OCID de la tenancy"),
            ("User OCID", "OCID del usuario técnico"),
            ("Fingerprint", "Huella de la API key"),
            ("Private Key", "Llave privada de la API key"),
        ]

    return extension_id, rows


def _add_registration(document, number, app, settings, bullet, info_box):

    registrable = [b for b in app["backends"] if _registrable(b)]

    target = settings["target"]

    create_header(
        document,
        f"{number}\tMatriculación de los backends en el ERP destino "
        f"({target})",
        size=11
    )

    _text(
        document,
        "Antes de desplegar la aplicación, cada backend debe matricularse "
        f"en el ERP {target} con la configuración que apunta a los "
        f"servicios de {target}. La matriculación se realiza en la página "
        "de administración de backends (trap-admin) del ERP y se ejecuta "
        "una vez por ambiente."
    )

    _important(
        info_box,
        document,
        "El usuario de ERP Cloud debe tener el rol "
        "ORA_FND_ADMINISTRATOR_JOB o ORA_FND_APPLICATION_DEVELOPER_JOB. "
        "Con solo el privilegio ORA_FND_TRAP_PRIV la página se puede "
        "consultar, pero no se pueden crear registros."
    )

    for backend in registrable:

        auth = backend.get("auth")

        title = (
            f"Backend: {backend['label']} ({backend['id']}) - "
            f"{_auth_label(auth)}"
        )

        if backend["server_kind"] == "reference":
            backend = dict(backend, id=backend.get("reference"))
            title += f" - apunta a {backend['id']}"

        _text(document, title, bold=True, size=11, space_before=12)

        if not auth:
            _text(
                document,
                "No se indicó el método de autenticación de este backend. "
                "Complete los valores según el método que use el ambiente "
                "destino.",
                size=9,
                color=RGBColor(0xC0, 0x00, 0x00)
            )

        step = 1

        if (
            auth in CONFIDENTIAL_GRANTS
            or auth in ("oauth2_user_assertion", "oci_signature")
        ):
            _add_identity_steps(
                document, app, backend, settings, bullet, info_box
            )
            step += 1

        extension_id, rows = _registration_rows(app, backend, settings)

        _step(
            document,
            f"{step}. Acceso a la página de backends del ERP {target}"
        )

        _text(
            document,
            "Ingrese con un usuario del ERP destino a la siguiente dirección:"
        )

        _table(
            document,
            ["Ambiente", "URL"],
            [(
                target,
                f"{settings['erp']}/fscmUI/redwood/tools/trap-admin"
                f"?backendKey={extension_id}%3A{backend['id']}"
            )],
            title="Página de matriculación de backends"
        )

        _text(
            document,
            "Si el backend aún no está matriculado, la lista de la izquierda "
            "muestra \"No items to display\". Haga clic en Create para "
            "iniciar el registro."
        )

        step += 1

        _step(document, f"{step}. Registro del backend")

        _text(
            document,
            "Complete las secciones General information, Authentication "
            "details y Token details con los siguientes valores. El ID de "
            "extensión y el nombre del backend deben coincidir exactamente "
            "con los definidos en la aplicación."
        )

        _table(
            document,
            ["Campo", target],
            rows,
            title=f"Backend: {backend['id']}"
        )

        _text(
            document,
            "Agregue en Secure Headers / Custom Parameters solo los "
            "parámetros que el servicio requiera y haga clic en Update "
            "para guardar el registro."
        )

        step += 1

        _step(document, f"{step}. Validación del registro")

        _text(
            document,
            f"Verifique que el backend {backend['id']} del ID de extensión "
            f"{extension_id} figure en la lista de la página con la URL "
            "del ambiente. La configuración puede tardar hasta cinco "
            "minutos en tomar efecto."
        )

        note = AUTH_NOTES.get(auth)

        if note:
            info_box(document, "Nota", note)
            document.add_paragraph("")


# =========================================================
# JOB DE DESPLIEGUE Y DESPLIEGUE
# =========================================================

def _add_deploy_job(document, number, app, settings):

    repository = _repository(app, settings)

    target = settings["target"]

    create_header(
        document,
        f"{number}\tConfiguración del job de despliegue a {target}",
        size=11
    )

    _text(
        document,
        "El despliegue se realiza con los jobs del proyecto: el job de "
        "empaquetado (Package) genera el artefacto desde la rama main del "
        f"repositorio {repository} y el job Deploy_{target} lo instala en "
        f"el ERP {target}. Esta configuración se realiza una sola vez."
    )

    _step(document, "1. Revisión de los jobs")

    _text(
        document,
        "En el proyecto, seleccione Builds > Jobs y ubique los jobs del "
        f"repositorio {repository}. Si el job Deploy_{target} no existe, "
        "créelo con los siguientes valores:"
    )

    _table(
        document,
        ["Job", "Paso (Steps)", "Configuración"],
        [
            (
                "Package",
                "Application Extension Package",
                f"Repositorio: {repository} / Rama: main."
            ),
            (
                f"Deploy_{target}",
                "Application Extension Deploy",
                f"Instancia: {target} ({settings['erp']}). Artefacto: el "
                "generado por el job Package."
            )
        ],
        title="Jobs de publicación"
    )

    _step(document, "2. Credenciales del job de despliegue")

    _text(
        document,
        f"Abra la configuración del job Deploy_{target} y verifique que "
        f"tenga registradas las credenciales de un usuario del ERP {target} "
        "(no de Visual Builder Studio ni de SSO). Si no las tiene, se "
        "solicitarán en la primera ejecución y quedarán guardadas en el job."
    )

    _text(
        document,
        f"El job Deploy_{target} no forma parte del pipeline automático: se "
        "ejecuta manualmente una vez certificada la aplicación en "
        f"{settings['source']}."
    )


def _add_deploy(document, number, app, settings, registration_number,
                bullet, info_box):

    target = settings["target"]

    create_header(
        document,
        f"{number}\tDespliegue de la aplicación en {target}",
        size=11
    )

    if registration_number:
        _important(
            info_box,
            document,
            "Antes de desplegar, verifique que los backends estén "
            f"matriculados en el ERP {target} (sección "
            f"{registration_number}). Si no lo están, la aplicación se "
            "desplegará, pero no podrá invocar sus servicios."
        )

    _step(document, "1. Ejecución del despliegue")

    _text(
        document,
        f"Seleccione Builds > Jobs, ubique el job Deploy_{target} y haga "
        f"clic en Build Now. El job despliega en {target} el mismo "
        f"artefacto certificado en {settings['source']}."
    )

    _step(document, "2. Seguimiento")

    _text(
        document,
        f"Verifique que el job Deploy_{target} finalice con estado "
        "Succeeded. Si falla, revise su registro (Log) antes de reintentar."
    )

    _step(document, "3. Validación del despliegue")

    _text(
        document,
        f"En Environments > Extension Lifecycle, en el ambiente {target}, "
        "verifique que la extensión "
        f"{app.get('extension_name') or ''} figure con estado Live y "
        f"versión {app.get('extension_version') or '<versión>'}."
        "<número de build>. Luego ingrese a la aplicación en el ERP y "
        "verifique que muestre información de los servicios del ambiente:"
    )

    for item in app.get("applications") or []:
        bullet(document, f"{settings['erp']}/fscmUI/redwood/{item['id']}")


# =========================================================
# GRUPO E ICONO DEL NAVEGADOR
# =========================================================

def _add_navigator(document, number, app, settings):

    target = settings["target"]

    names = app.get("applications") or [
        {"id": "<app>", "name": "<Aplicación>"}
    ]

    group = names[0]["name"]

    sandbox = _slug(group)

    create_header(
        document,
        f"{number}\tCreación del grupo y del icono: {group}",
        size=11
    )

    _text(
        document,
        f"Una vez desplegada la aplicación, se crea en el ERP {target} el "
        f"grupo \"{group}\" del Navegador y se registra dentro de él el "
        "icono de acceso a la aplicación."
    )

    _step(document, "1. Creación y activación del sandbox")

    _text(
        document,
        "Ingrese a Navegador > Configuración > Sandboxes y cree un sandbox "
        f"con el nombre {sandbox}, seleccionando la herramienta Estructura. "
        "Luego seleccione Entrar al sandbox."
    )

    _step(document, "2. Acceso a la herramienta Estructura")

    _text(
        document,
        "Con el sandbox activo, ingrese a Navegador > Configuración > "
        "Estructura."
    )

    _step(document, "3. Creación del grupo")

    _text(
        document,
        "Seleccione Crear > Crear grupo, complete los siguientes valores y "
        "seleccione Guardar y cerrar."
    )

    _table(
        document,
        ["Campo", "Valor"],
        [
            ("Nombre", group),
            ("Icono", "Seleccione un icono de la galería"),
            ("Mostrar en", "Navegador y página de inicio"),
        ],
        title="Grupo"
    )

    _step(document, "4. Creación del icono de la aplicación")

    _text(
        document,
        "Seleccione Crear > Crear entrada de página, complete los "
        "siguientes valores y seleccione Guardar y cerrar."
    )

    for item in names:

        _table(
            document,
            ["Campo", "Valor"],
            [
                ("Nombre", item["name"]),
                ("Icono", "Seleccione un icono de la galería"),
                ("Grupo", group),
                ("Tipo de enlace", "URL estática"),
                ("URL de destino",
                 f"{settings['erp']}/fscmUI/redwood/{item['id']}"),
                ("Mostrar en", "Navegador y página de inicio"),
            ],
            title="Entrada de página"
        )

    _step(document, "5. Publicación del sandbox")

    _text(
        document,
        "Regrese a Navegador > Configuración > Sandboxes, seleccione el "
        f"sandbox {sandbox} y elija Publicar."
    )

    _step(document, "6. Validación final de la aplicación")

    _text(
        document,
        "Cierre sesión y vuelva a ingresar a ERP Cloud. Verifique que el "
        f"grupo \"{group}\" se visualice en el Navegador y que, al "
        "seleccionar el icono, se abra la aplicación."
    )


# =========================================================
# ENTRY POINT
# =========================================================

def add_vbs_installation_section(
    document,
    vbs_installation_plan
):

    if not vbs_installation_plan or not vbs_installation_plan.get("apps"):
        return

    bullet, info_box = _helpers()

    settings = _settings(vbs_installation_plan)

    apps = vbs_installation_plan["apps"]

    several = len(apps) > 1

    create_header(
        document,
        f"{SECTION_NUMBER}\tInstalación paso a paso de "
        + (
            "las aplicaciones de Visual Builder Studio"
            if several
            else "la aplicación de Visual Builder Studio"
        ),
        size=13
    )

    for app_index, app in enumerate(apps):

        prefix = (
            f"{SECTION_NUMBER}.{app_index + 1}"
            if several
            else SECTION_NUMBER
        )

        name = app.get("extension_name") or app["file_name"]

        if several:
            create_header(document, f"{prefix}\t{name}", size=12)

        document.add_paragraph(
            f"La aplicación {name} se mantiene en el proyecto de Oracle "
            "Visual Builder Studio (VBS) y se despliega al ambiente "
            f"{settings['target']} mediante el job de despliegue del "
            "proyecto. En esta sección se detallan las actividades para "
            "validar el proyecto, matricular sus backends en el ERP "
            "destino, desplegarla y publicarla en el Navegador de ERP Cloud."
        )

        _important(
            info_box,
            document,
            "Ejecute esta sección después de activar las integraciones de "
            "OIC (sección 3.3). La aplicación consume dichas integraciones "
            "y no funcionará si no se encuentran en estado \"Active\"."
        )

        _add_metadata(document, app, bullet, info_box)

        _add_environments(document, settings)

        has_registration = any(_registrable(b) for b in app["backends"])

        number = 1

        _add_access(document, f"{prefix}.{number}", settings, bullet)

        number += 1

        repository_number = number

        number += 1

        registration_number = (
            f"{prefix}.{number}" if has_registration else None
        )

        _add_repository(
            document, f"{prefix}.{repository_number}", app, settings,
            registration_number, bullet, info_box
        )

        if has_registration:

            _add_registration(
                document, registration_number, app, settings,
                bullet, info_box
            )

            number += 1

        _add_deploy_job(document, f"{prefix}.{number}", app, settings)

        number += 1

        _add_deploy(
            document, f"{prefix}.{number}", app, settings,
            registration_number, bullet, info_box
        )

        number += 1

        _add_navigator(document, f"{prefix}.{number}", app, settings)
