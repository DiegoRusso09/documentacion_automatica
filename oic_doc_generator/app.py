# =========================================================
# FILE:
# oic_doc_generator/app.py
# =========================================================

import os

import streamlit as st

from parsers.par_parser import (
    extract_package,
    get_par_binary_content_zip
)

from parsers.iar_parser import (
    get_iar_binary_content_zip
)

from generators.word_generator import (
    generate_word_document
)


# =========================================================
# CONFIG
# =========================================================

st.set_page_config(

    page_title=
        "Oracle Technical Documentation Generator",

    layout="wide"
)

st.title(
    "📘 Oracle Technical Documentation Generator"
)


# =========================================================
# GENERAL PARAMETERS
# =========================================================

st.header(
    "1. Información General"
)

author_name = st.text_input(
    "Autor del documento"
)

development_name = st.text_input(
    "Nombre del Desarrollo"
)


# =========================================================
# COMPONENTS
# =========================================================

st.subheader(
    "Componentes del Desarrollo"
)

use_visual_builder = st.checkbox(
    "Aplicación en Visual Builder"
)

use_apex = st.checkbox(
    "Aplicación de APEX"
)

use_oic = st.checkbox(
    "Paquete de OIC"
)

use_db = st.checkbox(
    "Objetos de BD"
)

use_bip = st.checkbox(
    "Reportes BI Publisher"
)


# =========================================================
# VISUAL BUILDER
# =========================================================

visual_builder_apps = []

if use_visual_builder:

    st.header(
        "2. Aplicaciones Visual Builder"
    )

    vb_files = st.file_uploader(

        "Subir archivos ZIP de Visual Builder",

        type=["zip"],

        accept_multiple_files=True,

        key="vb_files"
    )

    if vb_files:

        for idx, file in enumerate(vb_files):

            default_name = os.path.splitext(
                file.name
            )[0]

            app_name = st.text_input(

                f"Nombre aplicación Visual Builder: {file.name}",

                value=default_name,

                key=f"vb_name_{idx}"
            )

            try:

                # =========================================
                # STORE ZIP DIRECTLY
                # =========================================

                visual_builder_apps.append({

                    "name":
                        app_name,

                    "file":
                        file
                })

                st.success(
                    f"Aplicación "
                    f"{app_name} cargada correctamente."
                )

            except Exception as e:

                st.error(
                    f"Error procesando "
                    f"{file.name}: {str(e)}"
                )


# =========================================================
# APEX
# =========================================================

apex_apps = []

if use_apex:

    st.header(
        "3. Aplicaciones APEX"
    )

    apex_files = st.file_uploader(

        "Subir archivos de APEX",

        accept_multiple_files=True,

        key="apex_files"
    )

    if apex_files:

        for idx, file in enumerate(apex_files):

            default_name = os.path.splitext(
                file.name
            )[0]

            app_name = st.text_input(

                f"Nombre aplicación APEX: {file.name}",

                value=default_name,

                key=f"apex_name_{idx}"
            )

            apex_apps.append({

                "name":
                    app_name,

                "file":
                    file
            })


# =========================================================
# OIC SECTION
# =========================================================

uploaded_par = None

if use_oic:

    st.header(
        "4. Archivo PAR"
    )

    uploaded_par = st.file_uploader(

        "Subir archivo .par",

        type=["par"],

        key="par"
    )

    if uploaded_par:

        st.success(
            "Archivo PAR cargado correctamente."
        )

        try:

            par_binary_zip = (
                get_par_binary_content_zip(
                    uploaded_par
                )
            )

            st.download_button(

                label=
                    "⬇️ Descargar contenido binario del PAR",

                data=
                    par_binary_zip,

                file_name=
                    "par_binary_content.zip",

                mime=
                    "application/zip"
            )

        except Exception as e:

            st.error(
                f"Error leyendo PAR: {str(e)}"
            )


# =========================================================
# IAR SECTION
# =========================================================

uploaded_iar = None

if use_oic:

    st.header(
        "5. Archivo IAR"
    )

    uploaded_iar = st.file_uploader(

        "Subir archivo .iar",

        type=["iar"],

        key="iar"
    )

    if uploaded_iar:

        st.success(
            "Archivo IAR cargado correctamente."
        )

        try:

            iar_binary_zip = (
                get_iar_binary_content_zip(
                    uploaded_iar
                )
            )

            st.download_button(

                label=
                    "⬇️ Descargar contenido binario del IAR",

                data=
                    iar_binary_zip,

                file_name=
                    "iar_binary_content.zip",

                mime=
                    "application/zip"
            )

        except Exception as e:

            st.error(
                f"Error leyendo IAR: {str(e)}"
            )


# =========================================================
# GENERATE WORD
# =========================================================

st.header(
    "6. Generar Documento"
)

if st.button(
    "📘 Generar Word"
):

    with st.spinner(
        "Generando documentación..."
    ):

        try:

            package_path = None

            # =============================================
            # EXTRACT PAR
            # =============================================

            if use_oic and uploaded_par:

                package_path = extract_package(
                    uploaded_par
                )

            # =============================================
            # COMPONENTS
            # =============================================

            selected_components = []

            if use_visual_builder:

                selected_components.append(
                    "Visual Builder"
                )

            if use_apex:

                selected_components.append(
                    "APEX"
                )

            if use_oic:

                selected_components.append(
                    "OIC"
                )

            if use_db:

                selected_components.append(
                    "Objetos BD"
                )

            if use_bip:

                selected_components.append(
                    "BI Publisher"
                )

            # =============================================
            # NORMALIZE VB FILES
            # =============================================

            vb_zip_files = []

            for vb in visual_builder_apps:

                vb_file = vb.get(
                    "file"
                )

                if vb_file:

                    vb_zip_files.append(
                        vb_file
                    )

            # =============================================
            # GENERATE WORD
            # =============================================

            word_file = generate_word_document(

                package_path=
                    package_path,

                author_name=
                    author_name,

                development_name=
                    development_name,

                selected_components=
                    selected_components,

                visual_builder_apps=
                    vb_zip_files,

                apex_apps=
                    apex_apps,

                use_oic=
                    use_oic
            )

            st.success(
                "Documento generado correctamente."
            )

            st.download_button(

                label=
                    "⬇️ Descargar Word",

                data=
                    word_file,

                file_name=
                    "documentacion_tecnica.docx",

                mime=(
                    "application/vnd.openxmlformats-"
                    "officedocument.wordprocessingml."
                    "document"
                )
            )

        except Exception as e:

            st.error(
                f"Error generando documento: "
                f"{str(e)}"
            )