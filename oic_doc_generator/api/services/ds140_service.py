from pathlib import Path
from io import BytesIO

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
    create_job,
    complete_job,
    fail_job,
    initialize_progress,
    advance_progress,
    update_activity
)


def generate_ds140_service(
    job_id,
    author_name,
    development_name,
    files
):

    uploaded_par = None

    vb_files = []

    bip_files = []

    sql_files = []

    apex_apps = []

    for file in files:

        ext = Path(
            file.name
        ).suffix.lower()

        stream = file

        if ext == ".par":

            uploaded_par = stream

        elif ext == ".zip":

            vb_files.append(stream)

        elif ext in [
            ".xdoz",
            ".xdmz",
            ".xdrz"
        ]:

            bip_files.append(stream)

        elif ext == ".sql":

            sql_files.append(stream)

    package_path = None

    if uploaded_par:

        package_path = extract_package(
            uploaded_par
        )

    advance_progress(

        job_id,

        component="OIC",

        detail="Integraciones procesadas",

        object_name="Package"
    )

    database_metadata = None

    database_export_info = None

    if sql_files:

        database_metadata = (
            build_database_metadata(
                sql_files
            )
        )

        validation = (
            validate_sql_objects(
                database_metadata
            )
        )

        if not validation["valid"]:

            raise Exception(
                "\n".join(
                    validation["errors"]
                )
            )

        database_export_info = (
            export_database_sql(
                database_metadata
            )
        )

        advance_progress(

            job_id,

            component="OIC",

            detail="Integraciones procesadas",

            object_name="Package"
        )

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

            component="BI Publisher",

            detail="Reportes procesados",

            object_name="BIP"
        )

    selected_components = []

    if vb_files:

        selected_components.append(
            "Visual Builder"
        )

    if apex_apps:

        selected_components.append(
            "APEX"
        )

    if uploaded_par:

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

        package_path=package_path,

        author_name=author_name,

        development_name=development_name,

        selected_components=selected_components,

        visual_builder_apps=vb_files,

        apex_apps=apex_apps,

        bip_files=bip_files,

        database_metadata=database_metadata,

        database_export_info=database_export_info,

        job_id=job_id
    )

    # =====================================================
    # DELIVERY FOLDER
    # =====================================================

    delivery_folder = tempfile.mkdtemp(
        prefix="ds140_delivery_"
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
    ) as f:

        f.write(
            document_stream.getvalue()
        )

    # =====================================================
    # COPY SQL EXPORTS
    # =====================================================

    if database_export_info:

        sql_source = os.path.join(

            database_export_info["root"],

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

            for file in files:

                if file == "entrega.zip":

                    continue

                full_path = os.path.join(
                    root,
                    file
                )

                arcname = os.path.relpath(

                    full_path,

                    delivery_folder
                )

                zip_file.write(

                    full_path,

                    arcname
                )

    advance_progress(

        job_id,

        component="Entrega",

        detail="ZIP generado",

        object_name="entrega.zip"
    )

    complete_job(

        job_id,

        zip_path
    )

    return zip_path