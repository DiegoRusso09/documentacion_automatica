# =========================================================
# FILE:
# oic_doc_generator/api/services/im090_service.py
# =========================================================

import os
import shutil
import tempfile
import zipfile


from oic_doc_generator.backend.parsers.sql_object_parser import (
    build_database_metadata
)

from oic_doc_generator.backend.parsers.sql_conflict_validator import (
    validate_sql_objects
)

from oic_doc_generator.backend.utils.sql_exporter import (
    export_database_sql
)

from oic_doc_generator.backend.generators.installation_manual_generator import (
    generate_installation_manual
)

from oic_doc_generator.api.job_manager import (
    complete_job,
    advance_progress
)

from oic_doc_generator.backend.parsers.bip_archive_parser import (
    build_bip_artifact_tree,
    clean_bip_workspace
)

from oic_doc_generator.backend.parsers.bip_metadata_builder import (
    build_bip_metadata
)

from oic_doc_generator.backend.utils.bip_installation_plan import (
    build_bip_installation_plan
)

from oic_doc_generator.backend.utils.oic_installation_plan import (
    build_oic_installation_plan
)

# =========================================================
# EXPORT BIP DELIVERY FILES
# =========================================================

def export_bip_delivery_files(
    bip_files,
    delivery_folder
):

    if not bip_files:

        return None


    otbi_folder = os.path.join(
        delivery_folder,
        "OTBI"
    )


    os.makedirs(
        otbi_folder,
        exist_ok=True
    )


    used_names = set()


    for bip_file in bip_files:

        file_name = (
            os.path.basename(
                getattr(
                    bip_file,
                    "name",
                    ""
                )
            )
        )


        if not file_name:

            continue


        file_key = (
            file_name.lower()
        )


        if file_key in used_names:

            raise Exception(
                (
                    "Existen dos artefactos BI Publisher "
                    "con el mismo nombre de archivo: "
                    f"{file_name}"
                )
            )


        used_names.add(
            file_key
        )


        try:

            bip_file.seek(
                0
            )

        except Exception:

            pass


        content = (
            bip_file.read()
        )


        file_path = os.path.join(
            otbi_folder,
            file_name
        )


        with open(
            file_path,
            "wb"
        ) as target:

            target.write(
                content
            )


        try:

            bip_file.seek(
                0
            )

        except Exception:

            pass


    return otbi_folder

# =========================================================
# VALIDATE DATABASE INSTALLATION PLAN
# =========================================================

def validate_database_installation_plan(
    database_export_info
):

    if not database_export_info:

        return


    installation_scripts = (
        database_export_info.get(
            "installation_scripts",
            []
        )
    )


    scripts_folder = (
        database_export_info.get(
            "scripts_folder"
        )
    )


    if not installation_scripts:

        raise Exception(
            "No se generó el plan de instalación "
            "de Base de Datos."
        )


    if (
        not scripts_folder
        or
        not os.path.isdir(
            scripts_folder
        )
    ):

        raise Exception(
            "No se encontró la carpeta scripts "
            "generada para el IM090."
        )


    expected_order = 1


    for script in installation_scripts:

        order = script.get(
            "order"
        )


        file_name = (
            script.get(
                "file_name",
                ""
            )
            or
            ""
        ).strip()


        file_path = (
            script.get(
                "file_path",
                ""
            )
            or
            ""
        ).strip()


        # =================================================
        # ORDER
        # =================================================

        if order != expected_order:

            raise Exception(
                (
                    "Orden de instalación inválido. "
                    f"Se esperaba {expected_order} "
                    f"y se encontró {order}."
                )
            )


        # =================================================
        # FILE NAME
        # =================================================

        expected_prefix = (
            f"{expected_order}_"
        )


        if not file_name.startswith(
            expected_prefix
        ):

            raise Exception(
                (
                    "El archivo de instalación "
                    f"{file_name} no coincide con "
                    f"el orden {expected_order}."
                )
            )


        # =================================================
        # FILE EXISTS
        # =================================================

        if not file_path:

            file_path = os.path.join(
                scripts_folder,
                file_name
            )


        if not os.path.isfile(
            file_path
        ):

            raise Exception(
                (
                    "No se encontró el script "
                    f"de instalación: {file_name}"
                )
            )


        # =================================================
        # FILE NOT EMPTY
        # =================================================

        if os.path.getsize(
            file_path
        ) == 0:

            raise Exception(
                (
                    "El script de instalación "
                    f"{file_name} está vacío."
                )
            )


        expected_order += 1


# =========================================================
# VALIDATE IM090 ZIP
# =========================================================

def validate_im090_zip(
    zip_path,
    database_export_info=None
):

    if not os.path.isfile(
        zip_path
    ):

        raise Exception(
            "No se generó el ZIP del IM090."
        )


    expected_files = {
        "IM.090 Instrucciones de Instalación.docx"
    }


    if database_export_info:

        installation_scripts = (
            database_export_info.get(
                "installation_scripts",
                []
            )
        )


        for script in installation_scripts:

            file_name = (
                script.get(
                    "file_name",
                    ""
                )
                or
                ""
            ).strip()


            if file_name:

                expected_files.add(
                    f"scripts/{file_name}"
                )


    with zipfile.ZipFile(
        zip_path,
        "r"
    ) as zip_file:

        zip_files = set(
            zip_file.namelist()
        )


    missing_files = (
        expected_files
        -
        zip_files
    )


    if missing_files:

        missing_text = ", ".join(
            sorted(
                missing_files
            )
        )

        raise Exception(
            (
                "El paquete IM090 está incompleto. "
                "No se encontraron los siguientes "
                f"archivos: {missing_text}"
            )
        )


# =========================================================
# EXPORT OIC DELIVERY FILES
# =========================================================

def export_oic_delivery_files(
    oic_files,
    delivery_folder
):

    if not oic_files:

        return None


    oic_folder = os.path.join(
        delivery_folder,
        "OIC"
    )


    os.makedirs(
        oic_folder,
        exist_ok=True
    )


    used_names = set()


    for oic_file in oic_files:

        file_name = (
            os.path.basename(
                getattr(
                    oic_file,
                    "name",
                    ""
                )
            )
        )


        if not file_name:

            continue


        # =================================================
        # VALIDATE EXTENSION
        # =================================================

        lower_name = (
            file_name.lower()
        )


        if not (
            lower_name.endswith(
                ".iar"
            )
            or
            lower_name.endswith(
                ".par"
            )
        ):

            continue


        # =================================================
        # DUPLICATE NAME
        # =================================================

        file_key = (
            file_name.lower()
        )


        if file_key in used_names:

            raise Exception(
                (
                    "Existen dos artefactos OIC "
                    "con el mismo nombre de archivo: "
                    f"{file_name}"
                )
            )


        used_names.add(
            file_key
        )


        # =================================================
        # RESET
        # =================================================

        try:

            oic_file.seek(
                0
            )

        except Exception:

            pass


        # =================================================
        # READ
        # =================================================

        content = (
            oic_file.read()
        )


        # =================================================
        # WRITE
        # =================================================

        file_path = os.path.join(
            oic_folder,
            file_name
        )


        with open(
            file_path,
            "wb"
        ) as target:

            target.write(
                content
            )


        # =================================================
        # RESET AGAIN
        # =================================================

        try:

            oic_file.seek(
                0
            )

        except Exception:

            pass


    return oic_folder

# =========================================================
# GENERATE IM090
# =========================================================

def generate_im090_service(

    job_id,

    author_name,

    development_name,

    schema_name,

    vb_files=None,

    apex_files=None,

    oic_files=None,

    bip_files=None,

    sql_files=None,

    erp_roles=None,

    reviewers=None,

    approvers=None
):

    # =====================================================
    # NORMALIZE
    # =====================================================

    vb_files = (
        vb_files
        or
        []
    )

    apex_files = (
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

    erp_roles = (
        erp_roles
        or
        []
    )

    reviewers = (
        reviewers
        or
        []
    )

    approvers = (
        approvers
        or
        []
    )


    # =====================================================
    # SELECTED COMPONENTS
    # =====================================================

    selected_components = []


    if vb_files:

        selected_components.append(
            "Visual Builder"
        )


    if apex_files:

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
    # DATABASE
    # =====================================================

    database_metadata = None

    database_export_info = None

    oic_installation_plan = None


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


        if not validation[
            "valid"
        ]:

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

        validate_database_installation_plan(
            database_export_info
        )


        advance_progress(

            job_id,

            component=
                "IM090 - Base de Datos",

            detail=
                "Plan de instalación generado",

            object_name=
                f"{len(sql_files)} archivo(s)"
        )


    # =========================================================
    # BI PUBLISHER
    # =========================================================

    bip_installation_plan = None


    if bip_files:

        artifact_tree = None


        try:

            # =================================================
            # RESET STREAMS
            # =================================================

            for bip_file in bip_files:

                try:

                    bip_file.seek(
                        0
                    )

                except Exception:

                    pass


            # =================================================
            # ARTIFACT TREE
            # =================================================

            artifact_tree = (
                build_bip_artifact_tree(
                    bip_files
                )
            )


            # =================================================
            # METADATA
            # =================================================

            bip_metadata = (
                build_bip_metadata(
                    artifact_tree
                )
            )


            # =================================================
            # INSTALLATION PLAN
            # =================================================

            bip_installation_plan = (
                build_bip_installation_plan(

                    artifact_tree,

                    bip_metadata
                )
            )


            installation_items = (
                bip_installation_plan.get(
                    "items",
                    []
                )
            )


            if not installation_items:

                raise Exception(
                    (
                        "No fue posible generar el plan "
                        "de instalación de BI Publisher."
                    )
                )


            # =================================================
            # ROUTES MUST BE RESOLVED
            # =================================================

            unresolved = [

                item.get(
                    "file_name",
                    ""
                )

                for item in installation_items

                if not item.get(
                    "route_resolved",
                    False
                )
            ]


            if unresolved:

                raise Exception(
                    (
                        "No fue posible determinar la ruta "
                        "de instalación de los siguientes "
                        "artefactos BI Publisher: "
                        +
                        ", ".join(
                            unresolved
                        )
                    )
                )


            advance_progress(

                job_id,

                component=
                    "IM090 - BI Publisher",

                detail=
                    "Plan de instalación generado",

                object_name=
                    f"{len(installation_items)} artefacto(s)"
            )


        finally:

            if artifact_tree:

                clean_bip_workspace(
                    artifact_tree.get(
                        "workspace"
                    )
                )


    # =========================================================
    # OIC
    # =========================================================

    if oic_files:

        # =====================================================
        # RESET FILE STREAMS
        # =====================================================

        for oic_file in oic_files:

            try:

                oic_file.seek(
                    0
                )

            except Exception:

                pass


        # =====================================================
        # BUILD INSTALLATION PLAN
        # =====================================================

        oic_installation_plan = (
            build_oic_installation_plan(
                oic_files
            )
        )


        installation_items = (
            oic_installation_plan.get(
                "items",
                []
            )
        )


        warnings = (
            oic_installation_plan.get(
                "warnings",
                []
            )
        )


        # =====================================================
        # VALIDATE
        # =====================================================

        if not installation_items:

            warning_text = (
                "\n".join(
                    warnings
                )
                if warnings
                else
                "No se detectaron artefactos IAR o PAR."
            )


            raise Exception(
                (
                    "No fue posible generar el plan "
                    "de instalación de OIC.\n"
                    f"{warning_text}"
                )
            )


        # =====================================================
        # LOG WARNINGS
        # =====================================================

        for warning in warnings:

            print(
                "[IM090][OIC][WARNING]",
                warning
            )


        # =====================================================
        # RESET AGAIN
        # =====================================================

        for oic_file in oic_files:

            try:

                oic_file.seek(
                    0
                )

            except Exception:

                pass


        advance_progress(

            job_id,

            component=
                "IM090 - OIC",

            detail=
                "Plan de instalación generado",

            object_name=
                f"{len(installation_items)} artefacto(s)"
        )

    # =====================================================
    # GENERATE WORD
    # =====================================================

    document_stream = (
        generate_installation_manual(

            author_name=
                author_name,

            oic_installation_plan=
                oic_installation_plan,

            development_name=
                development_name,

            bip_installation_plan=
                bip_installation_plan,

            selected_components=
                selected_components,

            erp_roles=
                erp_roles,

            reviewers=
                reviewers,

            approvers=
                approvers,

            schema_name=
                schema_name,

            database_export_info=
                database_export_info
        )
    )


    advance_progress(

        job_id,

        component=
            "IM090",

        detail=
            "Documento generado",

        object_name=
            "IM.090 Instrucciones de Instalación.docx"
    )


    # =====================================================
    # DELIVERY FOLDER
    # =====================================================

    delivery_folder = (
        tempfile.mkdtemp(
            prefix=
                "im090_delivery_"
        )
    )

    # =========================================================
    # COPY BI PUBLISHER ARTIFACTS
    # =========================================================

    export_bip_delivery_files(

        bip_files,

        delivery_folder
    )

    # =====================================================
    # COPY OIC ARTIFACTS
    # =====================================================

    export_oic_delivery_files(

        oic_files,

        delivery_folder
    )


    # =====================================================
    # SAVE WORD
    # =====================================================

    word_path = os.path.join(

        delivery_folder,

        "IM.090 Instrucciones de Instalación.docx"
    )


    with open(
        word_path,
        "wb"
    ) as file:

        file.write(
            document_stream.getvalue()
        )


    # =====================================================
    # COPY CONSOLIDATED SCRIPTS
    # =====================================================

    if database_export_info:

        scripts_source = (
            database_export_info.get(
                "scripts_folder"
            )
        )


        scripts_target = os.path.join(
            delivery_folder,
            "scripts"
        )


        if (
            scripts_source
            and
            os.path.exists(
                scripts_source
            )
        ):

            shutil.copytree(

                scripts_source,

                scripts_target,

                dirs_exist_ok=True
            )


    # =====================================================
    # ZIP DELIVERY
    # =====================================================

    zip_path = os.path.join(
        delivery_folder,
        "IM090_entrega.zip"
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
                    "IM090_entrega.zip"
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

    validate_im090_zip(
        zip_path,
        database_export_info
    )

    # =====================================================
    # COMPLETE
    # =====================================================

    advance_progress(

        job_id,

        component=
            "IM090",

        detail=
            "Paquete de instalación generado",

        object_name=
            "IM090_entrega.zip"
    )


    complete_job(
        job_id,
        zip_path
    )


    return zip_path