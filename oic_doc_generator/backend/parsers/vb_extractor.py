# =========================================================
# FILE:
# oic_doc_generator/parsers/vb_extractor.py
# =========================================================
#
# Lee el .zip exportado de Visual Builder. Soporta dos
# estructuras:
#
#   1) "classic"  - Visual Builder de OIC (descontinuado):
#        webApps/<app>/
#            pages/shell-page.html
#            flows/<flow>/pages/*-page.html
#            resources/css/app.css
#        services/<conexión>/openapi3.json
#        businessObjects/...
#
#   2) "extension" - Visual Builder Studio (App UI de
#      Oracle Fusion / ERP):
#        extension1/sources/extension.json
#        extension1/sources/ui/self/applications/<app>/
#            app.json
#            flows/<flow>/pages/*-page.html
#            resources/css/app.css
#        extension1/sources/services/self/catalog.json
#        extension1/sources/services/self/<svc>/openapi3.json
#
#   En "extension" no hay shell-page.html: la App UI se
#   muestra dentro del shell de Fusion, por eso shell_html
#   queda vacío y la pantalla se arma solo con la página.
# =========================================================

import os
import json
import zipfile
import tempfile


LAYOUT_CLASSIC = "classic"

LAYOUT_EXTENSION = "extension"


# =========================================================
# EXTRACT ZIP
# =========================================================

def extract_visual_builder_zip(
    uploaded_zip
):

    temp_dir = tempfile.mkdtemp(
        prefix="vb_extract_"
    )

    # =====================================================
    # CASE 1 - STRING PATH
    # =====================================================

    if isinstance(
        uploaded_zip,
        str
    ):

        zip_path = uploaded_zip

    # =====================================================
    # CASE 2 - PATH OBJECT
    # =====================================================

    elif hasattr(
        uploaded_zip,
        "__fspath__"
    ):

        zip_path = os.fspath(
            uploaded_zip
        )

    # =====================================================
    # CASE 3 - FILE OBJECT
    # =====================================================

    else:

        uploaded_zip.seek(0)

        temp_zip_path = os.path.join(
            temp_dir,
            "uploaded_vb.zip"
        )

        with open(
            temp_zip_path,
            "wb"
        ) as temp_file:

            temp_file.write(
                uploaded_zip.read()
            )

        zip_path = temp_zip_path

    # =====================================================
    # VALIDATE ZIP
    # =====================================================

    if not os.path.exists(
        zip_path
    ):

        raise Exception(
            f"ZIP no encontrado: {zip_path}"
        )

    # =====================================================
    # EXTRACT
    # =====================================================

    with zipfile.ZipFile(
        zip_path,
        "r"
    ) as zip_ref:

        zip_ref.extractall(
            temp_dir
        )

    print(
        f"[VB_EXTRACTOR] ZIP extraído en: {temp_dir}"
    )

    return temp_dir


# =========================================================
# FIND WEBAPPS FOLDER (CLASSIC - OIC)
# =========================================================

def find_webapps_folder(
    extracted_root
):

    for root, dirs, files in os.walk(
        extracted_root
    ):

        for directory in dirs:

            if directory == "webApps":

                webapps_path = os.path.join(
                    root,
                    directory
                )

                print(
                    f"[VB_EXTRACTOR] webApps encontrado: {webapps_path}"
                )

                return webapps_path

    print(
        "[VB_EXTRACTOR] webApps no encontrado"
    )

    return None


# =========================================================
# FIND APPLICATIONS FOLDER (EXTENSION - VB STUDIO)
# =========================================================

def find_extension_applications_folder(
    extracted_root
):

    # Ruta esperada:
    #   <extensión>/sources/ui/self/applications
    for root, dirs, files in os.walk(
        extracted_root
    ):

        if "applications" not in dirs:

            continue

        parts = os.path.normpath(
            root
        ).split(os.sep)

        if parts[-2:] == ["ui", "self"]:

            applications_path = os.path.join(
                root,
                "applications"
            )

            print(
                "[VB_EXTRACTOR] applications (VB Studio) "
                f"encontrado: {applications_path}"
            )

            return applications_path

    # Respaldo: cualquier carpeta "applications" cuyas
    # subcarpetas tengan un app.json.
    for root, dirs, files in os.walk(
        extracted_root
    ):

        if os.path.basename(root) != "applications":

            continue

        for directory in dirs:

            if os.path.isfile(
                os.path.join(
                    root,
                    directory,
                    "app.json"
                )
            ):

                print(
                    "[VB_EXTRACTOR] applications (VB Studio) "
                    f"encontrado: {root}"
                )

                return root

    print(
        "[VB_EXTRACTOR] applications (VB Studio) no encontrado"
    )

    return None


# =========================================================
# DETECT LAYOUT
# =========================================================

def detect_vb_layout(
    extracted_root
):

    # Devuelve (layout, carpeta que contiene las apps)

    webapps_folder = find_webapps_folder(
        extracted_root
    )

    if webapps_folder:

        return (
            LAYOUT_CLASSIC,
            webapps_folder
        )

    applications_folder = (
        find_extension_applications_folder(
            extracted_root
        )
    )

    if applications_folder:

        return (
            LAYOUT_EXTENSION,
            applications_folder
        )

    return (
        None,
        None
    )


# =========================================================
# LIST APPLICATIONS
# =========================================================

def list_application_folders(
    webapps_folder
):

    if not webapps_folder:

        return []

    app_folders = []

    for item in os.listdir(
        webapps_folder
    ):

        full_path = os.path.join(
            webapps_folder,
            item
        )

        if os.path.isdir(
            full_path
        ):

            app_folders.append(
                full_path
            )

    app_folders.sort()

    return app_folders


# =========================================================
# FIND FIRST APPLICATION
# =========================================================

def find_application_folder(
    webapps_folder
):

    # Sirve para las dos estructuras: recibe webApps
    # (classic) o applications (VB Studio).

    app_folders = list_application_folders(
        webapps_folder
    )

    if len(app_folders) == 0:

        print(
            "[VB_EXTRACTOR] no se encontraron aplicaciones"
        )

        return None

    if len(app_folders) > 1:

        print(
            "[VB_EXTRACTOR] el zip trae "
            f"{len(app_folders)} aplicaciones; "
            "se documenta la primera"
        )

    selected = app_folders[0]

    print(
        f"[VB_EXTRACTOR] aplicación seleccionada: {selected}"
    )

    return selected


# =========================================================
# GET RESOURCES PATH
# =========================================================

def get_resources_path(
    application_folder
):

    resources_path = os.path.join(
        application_folder,
        "resources"
    )

    if not os.path.exists(
        resources_path
    ):

        print(
            "[VB_EXTRACTOR] resources no encontrado"
        )

        return None

    print(
        f"[VB_EXTRACTOR] resources encontrado: {resources_path}"
    )

    return resources_path


# =========================================================
# GET IMAGES PATH
# =========================================================

def get_images_path(
    application_folder
):

    resources_path = get_resources_path(
        application_folder
    )

    if not resources_path:

        return None

    images_path = os.path.join(
        resources_path,
        "images"
    )

    if not os.path.exists(
        images_path
    ):

        print(
            "[VB_EXTRACTOR] images no encontrado"
        )

        return None

    print(
        f"[VB_EXTRACTOR] images encontrado: {images_path}"
    )

    return images_path


# =========================================================
# GET APP CSS
# =========================================================

def get_app_css_path(
    application_folder
):

    css_path = os.path.join(

        application_folder,

        "resources",

        "css",

        "app.css"
    )

    if not os.path.exists(
        css_path
    ):

        print(
            "[VB_EXTRACTOR] app.css no encontrado"
        )

        return None

    print(
        f"[VB_EXTRACTOR] app.css encontrado: {css_path}"
    )

    return css_path


# =========================================================
# READ FILE
# =========================================================

def read_text_file(
    file_path
):

    if not file_path:

        return ""

    if not os.path.exists(
        file_path
    ):

        return ""

    encodings = [

        "utf-8",

        "latin-1"
    ]

    for encoding in encodings:

        try:

            with open(

                file_path,

                "r",

                encoding=encoding
            ) as file:

                return file.read()

        except:

            pass

    return ""


# =========================================================
# READ JSON
# =========================================================

def read_json_file(
    file_path
):

    text = read_text_file(
        file_path
    )

    if not text:

        return {}

    try:

        data = json.loads(
            text
        )

    except ValueError:

        return {}

    return data if isinstance(data, dict) else {}


# =========================================================
# GET SHELL HTML
# =========================================================

def get_shell_html(
    application_folder,
    layout=LAYOUT_CLASSIC
):

    if layout == LAYOUT_EXTENSION:

        # Las App UI de VB Studio no tienen shell propio:
        # se muestran dentro del shell de Fusion.
        print(
            "[VB_EXTRACTOR] App UI de VB Studio: sin shell-page"
        )

        return ""

    pages_folder = os.path.join(
        application_folder,
        "pages"
    )

    if not os.path.exists(
        pages_folder
    ):

        print(
            "[VB_EXTRACTOR] pages folder no encontrado"
        )

        return ""

    shell_path = os.path.join(
        pages_folder,
        "shell-page.html"
    )

    if not os.path.exists(
        shell_path
    ):

        print(
            "[VB_EXTRACTOR] shell-page.html no encontrado"
        )

        return ""

    print(
        f"[VB_EXTRACTOR] shell encontrado: {shell_path}"
    )

    return read_text_file(
        shell_path
    )


# =========================================================
# EXTENSION INFO (VB STUDIO)
# =========================================================

def get_extension_info(
    applications_folder,
    application_folder
):

    # applications -> self -> ui -> sources
    sources_folder = os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                applications_folder
            )
        )
    )

    extension = read_json_file(
        os.path.join(
            sources_folder,
            "extension.json"
        )
    )

    app = read_json_file(
        os.path.join(
            application_folder,
            "app.json"
        )
    )

    services_folder = os.path.join(
        sources_folder,
        "services",
        "self"
    )

    return {

        "sources_folder":
            sources_folder,

        "services_folder":
            services_folder
            if os.path.isdir(services_folder)
            else None,

        "extension_id":
            extension.get("id", ""),

        "extension_name":
            extension.get("name", ""),

        "extension_version":
            extension.get("version", ""),

        "app_id":
            app.get(
                "id",
                os.path.basename(application_folder)
            ),

        "default_flow":
            app.get("defaultFlow", "")
    }


# =========================================================
# BUILD EXTRACTION METADATA
# =========================================================

def build_extraction_metadata(
    uploaded_zip
):

    extracted_root = extract_visual_builder_zip(
        uploaded_zip
    )

    layout, apps_container = detect_vb_layout(
        extracted_root
    )

    if not apps_container:

        raise Exception(
            "No se reconoce el zip de Visual Builder: "
            "no tiene webApps/ (VB de OIC) ni "
            "sources/ui/self/applications/ (VB Studio)"
        )

    application_folder = find_application_folder(
        apps_container
    )

    if not application_folder:

        raise Exception(
            "No se encontró aplicación VB"
        )

    shell_html = get_shell_html(
        application_folder,
        layout
    )

    app_css_path = get_app_css_path(
        application_folder
    )

    app_css = read_text_file(
        app_css_path
    )

    metadata = {

        "layout":
            layout,

        "root_path":
            extracted_root,

        # Se mantiene la clave por compatibilidad: en VB
        # Studio apunta a .../ui/self/applications
        "webapps_folder":
            apps_container,

        "application_folder":
            application_folder,

        "application_folders":
            list_application_folders(
                apps_container
            ),

        "resources_path":
            get_resources_path(
                application_folder
            ),

        "images_path":
            get_images_path(
                application_folder
            ),

        "app_css_path":
            app_css_path,

        "app_css":
            app_css,

        "shell_html":
            shell_html
    }

    if layout == LAYOUT_EXTENSION:

        metadata.update(
            get_extension_info(
                apps_container,
                application_folder
            )
        )

    print(
        f"[VB_EXTRACTOR] metadata generado correctamente ({layout})"
    )

    return metadata
