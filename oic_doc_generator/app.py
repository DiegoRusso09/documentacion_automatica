# =========================================================
# FILE:
# oic_doc_generator/app.py
# =========================================================

import os
import tempfile
import streamlit as st
import tempfile
import uuid

from oic_doc_generator.utils.sql_exporter import (
    create_delivery_zip
)

from oic_doc_generator.parsers.par_parser import (
    extract_package,
    get_par_binary_content_zip
)

from oic_doc_generator.parsers.iar_parser import (
    get_iar_binary_content_zip
)

from oic_doc_generator.generators.word_generator import (
    generate_word_document
)

from oic_doc_generator.parsers.bip_archive_parser import (
    build_bip_artifact_tree
)

from oic_doc_generator.parsers.bip_metadata_builder import (
    build_bip_metadata
)

from oic_doc_generator.parsers.sql_object_parser import (
    build_database_metadata
)

from oic_doc_generator.parsers.sql_conflict_validator import (
    validate_sql_objects
)

from oic_doc_generator.utils.sql_exporter import (
    export_database_sql
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
# BI PUBLISHER
# =========================================================

bip_files = []

if use_bip:

    st.header(
        "6. Reportes BI Publisher"
    )

    st.markdown(
        """
        Puede subir:

        - Reportes `.xdoz`
        - Data Models `.xdmz`
        - Carpetas `.xdrz`
        """
    )

    uploaded_bip_files = st.file_uploader(

        "Subir archivos BI Publisher",

        type=[

            "xdoz",

            "xdmz",

            "xdrz"
        ],

        accept_multiple_files=True,

        key="bip_files"
    )

    if uploaded_bip_files:

        bip_files = uploaded_bip_files

        st.success(
            f"{len(bip_files)} archivo(s) BI Publisher cargado(s)."
        )

        # =================================================
        # VALIDATE
        # =================================================

        try:

            artifact_tree = build_bip_artifact_tree(
                bip_files
            )

            bip_metadata = build_bip_metadata(
                artifact_tree
            )

            warnings = bip_metadata.get(
                "warnings",
                []
            )

            if warnings:

                st.warning(
                    "Se encontraron observaciones:"
                )

                for warning in warnings:

                    st.warning(
                        warning
                    )

            reports = bip_metadata.get(
                "reports",
                []
            )

            if reports:

                st.success(
                    f"Se detectaron "
                    f"{len(reports)} reporte(s)."
                )

                for report in reports:

                    st.info(

                        f"Reporte: "
                        f"{report.get('report_name','')} "
                        f"| DM: "
                        f"{report.get('data_model','NO ENCONTRADO')}"
                    )

        except Exception as e:

            st.error(
                f"Error procesando BI Publisher: "
                f"{str(e)}"
            )

# =========================================================
# DATABASE OBJECTS
# =========================================================

database_metadata = None

database_export_info = None

if use_db:

    st.header(
        "7. Objetos de Base de Datos"
    )

    uploaded_sql_files = st.file_uploader(

        "Subir archivos SQL",

        type=["sql"],

        accept_multiple_files=True,

        key="sql_files"
    )

    if uploaded_sql_files:

        try:

            database_metadata = (
                build_database_metadata(
                    uploaded_sql_files
                )
            )

            st.write(database_metadata)

            warnings = database_metadata.get(
                "warnings",
                []
            )

            for warning in warnings:

                st.warning(
                    warning
                )

            validation = (
                validate_sql_objects(
                    database_metadata
                )
            )

            if not validation["valid"]:

                for error in validation["errors"]:

                    st.error(error)

                st.stop()

            database_export_info = (
                export_database_sql(
                    database_metadata
                )
            )

            st.success(
                f"Se detectaron "
                f"{len(database_metadata.get('tables', []))} tabla(s), "
                f"{len(database_metadata.get('sequences', []))} secuencia(s) y "
                f"{len(database_metadata.get('packages', []))} paquete(s)."
            )

        except Exception as e:

            st.error(
                f"Error procesando SQL: "
                f"{str(e)}"
            )

# =========================================================
# GENERATE WORD
# =========================================================

st.header(
    "8. Generar Documento"
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

            if visual_builder_apps:

                selected_components.append(
                    "Visual Builder"
                )

            if apex_apps:

                selected_components.append(
                    "APEX"
                )

            if uploaded_par or uploaded_iar:

                selected_components.append(
                    "OIC"
                )

            if use_db:

                selected_components.append(
                    "Objetos BD"
                )

            if bip_files:

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

                bip_files=
                    bip_files,

                database_metadata=
                    database_metadata,

                database_export_info=
                    database_export_info
            )

            st.success(
                "Documento generado correctamente."
            )

            # =====================================================
            # ZIP DELIVERY
            # =====================================================

            if database_export_info:

                from oic_doc_generator.utils.sql_exporter import (
                    create_delivery_zip
                )

                import os

                delivery_folder = (
                    database_export_info["root"]
                )

                word_path = os.path.join(

                    delivery_folder,

                    "documentacion_tecnica.docx"
                )

                with open(
                    word_path,
                    "wb"
                ) as f:

                    f.write(
                        word_file.getvalue()
                    )

                zip_path = os.path.join(

                    tempfile.gettempdir(),

                    f"Entrega_{uuid.uuid4()}.zip"
                )

                create_delivery_zip(

                    delivery_folder,

                    zip_path
                )

                with open(
                    zip_path,
                    "rb"
                ) as f:

                    zip_bytes = f.read()

                st.download_button(

                    label=
                        "⬇️ Descargar Entrega",

                    data=
                        zip_bytes,

                    file_name=
                        "Entrega.zip",

                    mime=
                        "application/zip"
                )

            else:

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