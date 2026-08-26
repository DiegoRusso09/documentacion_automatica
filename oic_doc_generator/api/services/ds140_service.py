from pathlib import Path

import os
import shutil
import tempfile
import zipfile

from oic_doc_generator.backend.parsers.par_parser import (
    extract_package
)

from oic_doc_generator.backend.parsers.sql_object_parser import (
    build_database_metadata
)

from oic_doc_generator.backend.parsers.bip_archive_parser import (
    build_bip_artifact_tree
)

from oic_doc_generator.backend.parsers.bip_metadata_builder import (
    build_bip_metadata
)

from oic_doc_generator.backend.parsers.sql_conflict_validator import (
    validate_sql_objects
)

from oic_doc_generator.backend.utils.sql_exporter import (
    export_database_sql
)

from oic_doc_generator.backend.generators.word_generator import (
    generate_word_document
)

from oic_doc_generator.api.job_manager import (
    complete_job,
    advance_progress
)


# =========================================================
# GENERATE DS140
# =========================================================

def generate_ds140_service(

    job_id,

    author_name,

    development_name,

    vb_files,

    apex_files,

    oic_files,

    bip_files,

    sql_files
):

    # =====================================================
    # NORMALIZE
    # =====================================================

    vb_files = (
        vb_files
        or
        []
    )

    apex_apps = (
        apex_files
        or
        []
    )

    oic_files = (
        oic_files
        or
        []
    )

    bip_files = (
        bip_files
        or
        []
    )

    sql_files = (
        sql_files
        or
        []
    )


    # =====================================================
    # OIC
    # =====================================================

    package_path = None


    if oic_files:

        package_path = tempfile.mkdtemp(
            prefix="oic_package_"
        )


        for oic_file in oic_files:

            extension = Path(
                oic_file.name
            ).suffix.lower()


            # =================================================
            # PAR
            # =================================================

            if extension == ".par":

                oic_file.seek(
                    0
                )


                extracted_path = (
                    extract_package(
                        oic_file
                    )
                )


                # =============================================
                # COPY EXTRACTED PAR CONTENT
                # =============================================

                for root, dirs, files in os.walk(
                    extracted_path
                ):

                    for file_name in files:

                        source_path = os.path.join(
                            root,
                            file_name
                        )


                        relative_path = os.path.relpath(
                            source_path,
                            extracted_path
                        )


                        target_path = os.path.join(
                            package_path,
                            relative_path
                        )


                        os.makedirs(
                            os.path.dirname(
                                target_path
                            ),
                            exist_ok=True
                        )


                        shutil.copy2(
                            source_path,
                            target_path
                        )


            # =================================================
            # IAR
            # =================================================

            elif extension == ".iar":

                oic_file.seek(
                    0
                )


                target_path = os.path.join(

                    package_path,

                    os.path.basename(
                        oic_file.name
                    )
                )


                with open(
                    target_path,
                    "wb"
                ) as target_file:

                    target_file.write(
                        oic_file.read()
                    )


        advance_progress(

            job_id,

            component=
                "OIC",

            detail=
                "Integraciones procesadas",

            object_name=
                f"{len(oic_files)} archivo(s)"
        )


    # =====================================================
    # DATABASE
    # =====================================================

    database_metadata = None

    database_export_info = None


    if sql_files:

        database_metadata = (
            build_database_metadata(
                sql_files
            )
        )

        print(
            "[SQL METADATA]",
            {
                "tables":
                    len(
                        database_metadata.get(
                            "tables",
                            []
                        )
                    ),

                "sequences":
                    len(
                        database_metadata.get(
                            "sequences",
                            []
                        )
                    ),

                "packages":
                    len(
                        database_metadata.get(
                            "packages",
                            []
                        )
                    ),

                "views":
                    len(
                        database_metadata.get(
                            "views",
                            []
                        )
                    )
            }
        )

        validation = (
            validate_sql_objects(
                database_metadata
            )
        )


        if not validation["valid"]:

            raise Exception(

                "\n".join(
                    validation[
                        "errors"
                    ]
                )
            )


        database_export_info = (
            export_database_sql(
                database_metadata
            )
        )


        advance_progress(

            job_id,

            component=
                "Base de Datos",

            detail=
                "Objetos SQL procesados",

            object_name=
                f"{len(sql_files)} archivo(s)"
        )


    # =====================================================
    # BI PUBLISHER
    # =====================================================

    if bip_files:

        artifact_tree = (
            build_bip_artifact_tree(
                bip_files
            )
        )


        build_bip_metadata(
            artifact_tree
        )


        advance_progress(

            job_id,

            component=
                "BI Publisher",

            detail=
                "Reportes procesados",

            object_name=
                f"{len(bip_files)} archivo(s)"
        )


    # =====================================================
    # SELECTED COMPONENTS
    # =====================================================

    selected_components = []


    if vb_files:

        selected_components.append(
            "Visual Builder"
        )


    if apex_apps:

        selected_components.append(
            "APEX"
        )


    if oic_files:

        selected_components.append(
            "OIC"
        )


    if sql_files:

        selected_components.append(
            "Objetos BD"
        )


    if bip_files:

        selected_components.append(
            "BI Publisher"
        )


    # =====================================================
    # GENERATE WORD
    # =====================================================

    document_stream = generate_word_document(

        package_path=
            package_path,

        author_name=
            author_name,

        development_name=
            development_name,

        selected_components=
            selected_components,

        visual_builder_apps=
            vb_files,

        apex_apps=
            apex_apps,

        bip_files=
            bip_files,

        database_metadata=
            database_metadata,

        database_export_info=
            database_export_info,

        job_id=
            job_id
    )


    # =====================================================
    # DELIVERY FOLDER
    # =====================================================

    delivery_folder = tempfile.mkdtemp(
        prefix=
            "ds140_delivery_"
    )


    # =====================================================
    # SAVE WORD
    # =====================================================

    word_path = os.path.join(

        delivery_folder,

        "NEO-GD-IN-02 DS-140 Especificación de Diseño.docx"
    )


    with open(
        word_path,
        "wb"
    ) as file:

        file.write(
            document_stream.getvalue()
        )


    # =====================================================
    # COPY SQL EXPORTS
    # =====================================================

    if database_export_info:

        sql_source = os.path.join(

            database_export_info[
                "root"
            ],

            "SQL"
        )


        sql_target = os.path.join(

            delivery_folder,

            "SQL"
        )


        if os.path.exists(
            sql_source
        ):

            shutil.copytree(

                sql_source,

                sql_target,

                dirs_exist_ok=True
            )


    # =====================================================
    # ZIP DELIVERY
    # =====================================================

    zip_path = os.path.join(

        delivery_folder,

        "entrega.zip"
    )


    with zipfile.ZipFile(

        zip_path,

        "w",

        zipfile.ZIP_DEFLATED

    ) as zip_file:

        for root, dirs, files in os.walk(
            delivery_folder
        ):

            for file_name in files:

                if (
                    file_name
                    ==
                    "entrega.zip"
                ):

                    continue


                full_path = os.path.join(

                    root,

                    file_name
                )


                arcname = os.path.relpath(

                    full_path,

                    delivery_folder
                )


                zip_file.write(

                    full_path,

                    arcname
                )


    # =====================================================
    # COMPLETE
    # =====================================================

    advance_progress(

        job_id,

        component=
            "Entrega",

        detail=
            "ZIP generado",

        object_name=
            "entrega.zip"
    )


    complete_job(

        job_id,

        zip_path
    )


    return zip_path