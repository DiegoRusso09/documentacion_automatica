# =========================================================
# FILE:
# oic_doc_generator/parsers/vb_extractor.py
# =========================================================

import os
import zipfile
import tempfile


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
# FIND WEBAPPS FOLDER
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
# FIND FIRST APPLICATION
# =========================================================

def find_application_folder(
    webapps_folder
):

    if not webapps_folder:

        return None

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

    if len(app_folders) == 0:

        print(
            "[VB_EXTRACTOR] no se encontraron aplicaciones"
        )

        return None

    app_folders.sort()

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
# GET SHELL HTML
# =========================================================

def get_shell_html(
    application_folder
):

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
# BUILD EXTRACTION METADATA
# =========================================================

def build_extraction_metadata(
    uploaded_zip
):

    extracted_root = extract_visual_builder_zip(
        uploaded_zip
    )

    webapps_folder = find_webapps_folder(
        extracted_root
    )

    if not webapps_folder:

        raise Exception(
            "No se encontró webApps"
        )

    application_folder = find_application_folder(
        webapps_folder
    )

    if not application_folder:

        raise Exception(
            "No se encontró aplicación VB"
        )

    shell_html = get_shell_html(
        application_folder
    )

    app_css_path = get_app_css_path(
        application_folder
    )

    app_css = read_text_file(
        app_css_path
    )

    metadata = {

        "root_path":
            extracted_root,

        "webapps_folder":
            webapps_folder,

        "application_folder":
            application_folder,

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

    print(
        "[VB_EXTRACTOR] metadata generado correctamente"
    )

    return metadata