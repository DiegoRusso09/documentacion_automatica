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
    configure_steps,
    advance_step,
    complete_job,
    fail_job
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

    progress_steps = []

    if uploaded_par:

        progress_steps.append(
            "OIC"
        )

    if vb_files:

        progress_steps.append(
            "VB"
        )

    if bip_files:

        progress_steps.append(
            "BIP"
        )

    if sql_files:

        progress_steps.append(
            "SQL"
        )

    progress_steps.append(
        "WORD"
    )

    progress_steps.append(
        "ZIP"
    )

    configure_steps(

        job_id,

        progress_steps
    )

    if uploaded_par:

        package_path = extract_package(
            uploaded_par
        )

        advance_step(

            job_id,

            "Integraciones OIC Procesadas"
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

        advance_step(

            job_id,

            "Objetos Base de Datos Procesados"
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

        advance_step(

            job_id,

            "Reportes BI Publisher Procesados"
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

    advance_step(

        job_id,

        "Entrega ZIP Generada"
    )

    complete_job(

        job_id,

        zip_path
    )

    return zip_path