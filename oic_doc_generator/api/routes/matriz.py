# =========================================================
# FILE:
# oic_doc_generator/api/routes/matriz.py
# =========================================================

from io import BytesIO
from pathlib import Path
from typing import List, Optional

import os
import re
import shutil
import tempfile
import xml.etree.ElementTree as ET

import httpx

from fastapi import (
    APIRouter,
    File,
    Form,
    UploadFile
)

from fastapi import Query

from fastapi.responses import (
    JSONResponse,
    Response
)

from oic_doc_generator.backend.parsers.integration_parser import (
    get_integration_metadata as get_oic_integration_metadata,
    integration_is_scheduled
)

from oic_doc_generator.backend.parsers.bip_archive_parser import (
    build_bip_artifact_tree,
    clean_bip_workspace
)

from oic_doc_generator.backend.parsers.bip_metadata_builder import (
    build_bip_metadata
)

ORDS_MATRIZ_PDF_URL = (
    "https://sea27ktcsvagrmb-neodbaprod.adb.sa-saopaulo-1.oraclecloudapps.com"
    "/ords/neora/documentation-automation/matriz/pdf/"
)

from fastapi import Query

from fastapi.responses import (
    JSONResponse,
    Response
)

ORDS_MATRIZ_PDF_URL = (
    "https://sea27ktcsvagrmb-neodbaprod.adb.sa-saopaulo-1.oraclecloudapps.com"
    "/ords/neora/documentation-automation/matriz/pdf/"
)

from fastapi.responses import JSONResponse


# =========================================================
# PARSERS
# =========================================================

from oic_doc_generator.backend.parsers.par_parser import (
    extract_package
)

from oic_doc_generator.backend.parsers.iar_parser import (
    find_all_iar_files,
    extract_iar
)

from oic_doc_generator.backend.parsers.lookup_parser import (
    get_lookup_names
)

from oic_doc_generator.backend.utils.oic_installation_plan import (
    get_api_library_names
)

from oic_doc_generator.backend.parsers.project_parser import (
    get_project_name,
    get_project_version,
    get_integration_trigger_type
)

from oic_doc_generator.backend.parsers.schedule_parser import (
    is_scheduled_integration
)

from oic_doc_generator.backend.parsers.sql_object_parser import (
    build_database_metadata
)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter()


# =========================================================
# ORDS
# =========================================================

ORDS_MATRIZ_URL = (
    "https://sea27ktcsvagrmb-neodbaprod.adb.sa-saopaulo-1.oraclecloudapps.com"
    "/ords/neora/documentation-automation/matriz/"
)


# =========================================================
# HELPERS
# =========================================================

def safe_stem(
    file_name: str
) -> str:

    if not file_name:
        return ""

    return Path(
        file_name
    ).stem.strip()


# =========================================================
# UPLOADFILE -> BYTESIO
# =========================================================

async def to_memory_files(
    files: Optional[List[UploadFile]]
):

    result = []

    if not files:
        return result

    for uploaded_file in files:

        content = (
            await uploaded_file.read()
        )

        memory_file = BytesIO(
            content
        )

        memory_file.name = (
            uploaded_file.filename
            or
            "archivo"
        )

        memory_file.seek(
            0
        )

        result.append(
            memory_file
        )

    return result


# =========================================================
# OIC PACKAGE
# =========================================================

def extract_oic_package_name(
    extracted_iar: str
):

    candidate_tags = {
        "package",
        "packagename",
        "packageid",
        "packageidentifier"
    }

    candidate_attrs = {
        "package",
        "packagename",
        "packageid",
        "packageidentifier"
    }

    for root, dirs, files in os.walk(
        extracted_iar
    ):

        for file_name in files:

            if file_name.lower() != "project.xml":
                continue

            file_path = os.path.join(
                root,
                file_name
            )

            try:

                tree = ET.parse(
                    file_path
                )

                xml_root = tree.getroot()

                # =============================================
                # ATTRIBUTES
                # =============================================

                for key, value in xml_root.attrib.items():

                    normalized_key = (
                        key
                        .split("}")[-1]
                        .lower()
                    )

                    if (
                        normalized_key in candidate_attrs
                        and
                        value
                    ):

                        return value.strip()

                # =============================================
                # ELEMENTS
                # =============================================

                for element in xml_root.iter():

                    tag = (
                        element.tag
                        .split("}")[-1]
                        .lower()
                    )

                    if (
                        tag in candidate_tags
                        and
                        element.text
                        and
                        element.text.strip()
                    ):

                        return element.text.strip()

            except Exception:

                continue

    return None


# =========================================================
# BUILD OIC OBJECTS
# =========================================================

def build_oic_objects(
    oic_files
):

    objetos = []

    lookup_keys = set()
    library_keys = set()

    if not oic_files:
        return objetos


    temp_root = tempfile.mkdtemp(
        prefix="matriz_oic_"
    )

    cleanup_dirs = []


    try:

        for oic_file in oic_files:

            extension = (
                Path(
                    oic_file.name
                )
                .suffix
                .lower()
            )


            iar_files = []


            # =================================================
            # PAR
            # =================================================

            if extension == ".par":

                oic_file.seek(
                    0
                )

                package_path = (
                    extract_package(
                        oic_file
                    )
                )

                cleanup_dirs.append(
                    package_path
                )

                iar_files = (
                    find_all_iar_files(
                        package_path
                    )
                )


            # =================================================
            # IAR DIRECTO
            # =================================================

            elif extension == ".iar":

                oic_file.seek(
                    0
                )


                local_iar = os.path.join(

                    temp_root,

                    os.path.basename(
                        oic_file.name
                    )
                )


                with open(
                    local_iar,
                    "wb"
                ) as target:

                    target.write(
                        oic_file.read()
                    )


                iar_files = [
                    local_iar
                ]


            else:

                continue


            # =================================================
            # PROCESS EVERY IAR
            # =================================================

            for iar_path in iar_files:

                extracted_iar = (
                    extract_iar(
                        iar_path
                    )
                )


                cleanup_dirs.append(
                    extracted_iar
                )


                # =============================================
                # ORACLE METADATA
                # =============================================

                metadata = (
                    get_oic_integration_metadata(
                        extracted_iar
                    )
                )


                integration_id = (
                    metadata.get(
                        "project_code",
                        ""
                    )
                    or
                    ""
                ).strip()


                integration_name = (
                    metadata.get(
                        "project_name",
                        ""
                    )
                    or
                    ""
                ).strip()


                version = (
                    metadata.get(
                        "project_version",
                        ""
                    )
                    or
                    ""
                ).strip()


                # =============================================
                # ID ES OBLIGATORIO
                # =============================================

                if not integration_id:

                    print(
                        "[MATRIZ OIC] WARNING: "
                        "No se encontró project_code en:",
                        os.path.basename(
                            iar_path
                        )
                    )

                    continue


                # =============================================
                # NAME FALLBACK
                #
                # Sigue viniendo del metadata.
                # NO del filename.
                # =============================================

                if not integration_name:

                    integration_name = (
                        integration_id
                    )


                # =============================================
                # VERSION
                # =============================================

                if not version:

                    version = None


                # =============================================
                # INTEGRATION TYPE
                # =============================================

                scheduled = (
                    integration_is_scheduled(
                        metadata
                    )
                )


                # Fallback adicional al análisis estructural
                # del project.xml.
                if not scheduled:

                    scheduled = (
                        is_scheduled_integration(
                            extracted_iar
                        )
                    )


                if scheduled:

                    integration_type = (
                        "Integración Programada"
                    )


                else:

                    trigger_type = (
                        get_integration_trigger_type(
                            extracted_iar
                        )
                    )


                    trigger_type_map = {

                        "REST":
                            "Integración REST",

                        "SOAP":
                            "Integración SOAP",

                        "EVENT":
                            "Integración por Eventos"
                    }


                    integration_type = (
                        trigger_type_map.get(
                            trigger_type
                        )
                    )


                    if not integration_type:

                        print(
                            "[MATRIZ OIC] WARNING: "
                            "No se pudo determinar el tipo "
                            "de trigger de la integración:",
                            integration_name,
                            "| Trigger detectado:",
                            trigger_type
                        )

                        # No registramos un tipo falso.
                        continue


                print(
                    "[MATRIZ OIC] Tipo detectado:",
                    integration_name,
                    "=>",
                    integration_type
                )


                # =============================================
                # PACKAGE
                # =============================================

                package_name = (
                    extract_oic_package_name(
                        extracted_iar
                    )
                )


                # =============================================
                # MATRIX OBJECT
                # =============================================

                objeto = {

                    "id":
                        integration_id,

                    "nombre_objeto":
                        integration_name,

                    "tipo":
                        integration_type,

                    "version":
                        version,

                    "paquete":
                        package_name,

                    "creacion_modificacion":
                        "Creacion",

                    "herramienta":
                        "OIC",

                    "ruta":
                        None
                }


                objetos.append(
                    objeto
                )


                print(
                    "[MATRIZ OIC] Encontrado:",
                    objeto
                )

        # =============================================
        # LOOKUPS
        # =============================================

        lookup_names = (
            get_lookup_names(
                extracted_iar
            )
            or
            []
        )


        for lookup_name in lookup_names:

            lookup_name = (
                str(
                    lookup_name
                    or
                    ""
                ).strip()
            )


            if not lookup_name:

                continue


            lookup_key = (
                lookup_name.upper()
            )


            if lookup_key in lookup_keys:

                continue


            lookup_keys.add(
                lookup_key
            )


            lookup_object = {

                "id":
                    lookup_name,

                "nombre_objeto":
                    lookup_name,

                "tipo":
                    "Lookup",

                "version":
                    None,

                "paquete":
                    package_name,

                "creacion_modificacion":
                    "Creacion",

                "herramienta":
                    "OIC",

                "ruta":
                    None
            }


            objetos.append(
                lookup_object
            )


            print(
                "[MATRIZ OIC] Lookup encontrado:",
                lookup_object
            )


        # =============================================
        # JAVASCRIPT LIBRARIES
        # =============================================

        library_names = (
            get_api_library_names(
                extracted_iar
            )
            or
            []
        )


        for library_name in library_names:

            library_name = (
                str(
                    library_name
                    or
                    ""
                ).strip()
            )


            if not library_name:

                continue


            # El parser intenta obtener el nombre lógico
            # del api-library.
            #
            # Si tuvo que usar el .js como fallback,
            # quitamos únicamente la extensión.
            if library_name.lower().endswith(
                ".js"
            ):

                library_name = (
                    Path(
                        library_name
                    ).stem
                )


            library_name = (
                library_name.strip()
            )


            if not library_name:

                continue


            library_key = (
                library_name.upper()
            )


            if library_key in library_keys:

                continue


            library_keys.add(
                library_key
            )


            library_object = {

                "id":
                    library_name,

                "nombre_objeto":
                    library_name,

                "tipo":
                    "Biblioteca",

                "version":
                    None,

                "paquete":
                    package_name,

                "creacion_modificacion":
                    "Creacion",

                "herramienta":
                    "OIC",

                "ruta":
                    None
            }


            objetos.append(
                library_object
            )


            print(
                "[MATRIZ OIC] Biblioteca encontrada:",
                library_object
            )


    finally:

        for directory in cleanup_dirs:

            try:

                if (
                    directory
                    and
                    os.path.isdir(
                        directory
                    )
                ):

                    shutil.rmtree(
                        directory,
                        ignore_errors=True
                    )

            except Exception:

                pass


        shutil.rmtree(
            temp_root,
            ignore_errors=True
        )


    print(
        "[MATRIZ OIC] Total:",
        len(
            objetos
        )
    )


    return objetos

# =========================================================
# BUILD VISUAL BUILDER OBJECTS
# =========================================================

def build_vb_objects(
    vb_files
):

    objetos = []

    for vb_file in vb_files:

        name = safe_stem(
            vb_file.name
        )

        if not name:
            continue

        objetos.append({

            "id":
                name,

            "nombre_objeto":
                name,

            "tipo":
                None,

            "version":
                None,

            "paquete":
                None,

            "creacion_modificacion":
                "Creacion",

            "herramienta":
                "Visual Builder",

            "ruta":
                None
        })

    return objetos


# =========================================================
# BUILD BI PUBLISHER OBJECTS
# =========================================================

def build_bip_objects(
    bip_files
):

    objetos = []

    if not bip_files:
        return objetos


    artifact_tree = None


    try:

        # =================================================
        # REINICIAR STREAMS
        # =================================================

        for bip_file in bip_files:

            try:
                bip_file.seek(0)
            except Exception:
                pass


        # =================================================
        # ANALIZAR ARCHIVOS / CARPETAS XDRZ
        # =================================================

        artifact_tree = (
            build_bip_artifact_tree(
                bip_files
            )
        )


        # =================================================
        # METADATA DE REPORTES
        # =================================================

        bip_metadata = (
            build_bip_metadata(
                artifact_tree
            )
        )


        reports_metadata = (
            bip_metadata.get(
                "reports",
                []
            )
        )

        data_models_metadata = (
            bip_metadata.get(
                "data_models",
                []
            )
        )


        # =================================================
        # REPORTS
        # =================================================

        report_names = set()


        for report in reports_metadata:

            report_name = (
                report.get(
                    "report_name",
                    ""
                )
                or
                ""
            ).strip()


            if not report_name:
                continue


            report_path = (
                report.get(
                    "report_path"
                )
                or
                None
            )


            # Evitar duplicados
            report_key = (
                report_name.upper(),
                str(
                    report_path
                    or
                    ""
                ).upper()
            )


            if report_key in report_names:
                continue


            report_names.add(
                report_key
            )


            objetos.append({

                "id":
                    report_name,

                "nombre_objeto":
                    report_name,

                "tipo":
                    "Report",

                "version":
                    None,

                "paquete":
                    None,

                "creacion_modificacion":
                    "Creacion",

                "herramienta":
                    "BI Publisher",

                "ruta":
                    report_path
            })

        # =================================================
        # DATA MODELS
        # =================================================

        dm_names = set()


        for dm in data_models_metadata:

            # =============================================
            # NAME
            # =============================================

            dm_name = (
                dm.get(
                    "dm_name",
                    ""
                )
                or
                ""
            ).strip()


            if not dm_name:
                continue


            # =============================================
            # REAL BI PUBLISHER PATH
            # =============================================

            dm_path = (
                dm.get(
                    "dm_path",
                    ""
                )
                or
                ""
            ).strip()


            # =============================================
            # DUPLICATE CONTROL
            # =============================================

            dm_key = (
                dm_name.upper(),
                dm_path.upper()
            )


            if dm_key in dm_names:
                continue


            dm_names.add(
                dm_key
            )


            # =============================================
            # MATRIX OBJECT
            # =============================================

            objeto = {

                "id":
                    dm_name,

                "nombre_objeto":
                    dm_name,

                "tipo":
                    "Data Model",

                "version":
                    None,

                "paquete":
                    None,

                "creacion_modificacion":
                    "Creacion",

                "herramienta":
                    "BI Publisher",

                "ruta":
                    dm_path
            }


            objetos.append(
                objeto
            )


            # =============================================
            # LOG
            # =============================================

            print(
                "[MATRIZ BIP] Data Model:",
                dm_name,
                "| Ruta real:",
                dm_path
            )


        # =================================================
        # LOG
        # =================================================

        print(
            "[MATRIZ BIP] Reports encontrados:",
            len(
                report_names
            )
        )

        print(
            "[MATRIZ BIP] Data Models encontrados:",
            len(
                dm_names
            )
        )

        print(
            "[MATRIZ BIP] Total objetos:",
            len(
                objetos
            )
        )


        warnings = (
            artifact_tree.get(
                "warnings",
                []
            )
        )


        for warning in warnings:

            print(
                "[MATRIZ BIP] WARNING:",
                warning
            )


        return objetos


    finally:

        # =================================================
        # LIMPIAR WORKSPACE TEMPORAL
        # =================================================

        if artifact_tree:

            workspace = (
                artifact_tree.get(
                    "workspace"
                )
            )

            if workspace:

                clean_bip_workspace(
                    workspace
                )
                
# =========================================================
# BUILD DATABASE OBJECTS
# =========================================================

def build_database_objects(
    sql_files
):

    if not sql_files:
        return []

    for sql_file in sql_files:

        sql_file.seek(
            0
        )

    metadata = (
        build_database_metadata(
            sql_files
        )
    )

    objetos = []


    # =====================================================
    # TABLES
    # =====================================================

    for item in metadata.get(
        "tables",
        []
    ):

        name = item.get(
            "table_name",
            ""
        )

        if not name:
            continue

        objetos.append({

            "id":
                name,

            "nombre_objeto":
                name,

            "tipo":
                "Tabla",

            "version":
                None,

            "paquete":
                None,

            "creacion_modificacion":
                "Creacion",

            "herramienta":
                "BASE DE DATOS",

            "ruta":
                None
        })


    # =====================================================
    # SEQUENCES
    # =====================================================

    for item in metadata.get(
        "sequences",
        []
    ):

        name = item.get(
            "sequence_name",
            ""
        )

        if not name:
            continue

        objetos.append({

            "id":
                name,

            "nombre_objeto":
                name,

            "tipo":
                "Sequence",

            "version":
                None,

            "paquete":
                None,

            "creacion_modificacion":
                "Creacion",

            "herramienta":
                "BASE DE DATOS",

            "ruta":
                None
        })


    # =====================================================
    # PACKAGES
    # =====================================================

    for item in metadata.get(
        "packages",
        []
    ):

        name = item.get(
            "package_name",
            ""
        )

        if not name:
            continue

        objetos.append({

            "id":
                name,

            "nombre_objeto":
                name,

            "tipo":
                "Package",

            "version":
                None,

            "paquete":
                None,

            "creacion_modificacion":
                "Creacion",

            "herramienta":
                "BASE DE DATOS",

            "ruta":
                None
        })


    # =====================================================
    # VIEWS
    # =====================================================

    for item in metadata.get(
        "views",
        []
    ):

        name = item.get(
            "view_name",
            ""
        )

        if not name:
            continue

        objetos.append({

            "id":
                name,

            "nombre_objeto":
                name,

            "tipo":
                "View",

            "version":
                None,

            "paquete":
                None,

            "creacion_modificacion":
                "Creacion",

            "herramienta":
                "BASE DE DATOS",

            "ruta":
                None
        })


    # =====================================================
    # INDEXES
    # =====================================================

    for item in metadata.get(
        "indexes",
        []
    ):

        name = item.get(
            "index_name",
            ""
        )

        if not name:
            continue

        objetos.append({

            "id":
                name,

            "nombre_objeto":
                name,

            "tipo":
                "Index",

            "version":
                None,

            "paquete":
                None,

            "creacion_modificacion":
                "Creacion",

            "herramienta":
                "BASE DE DATOS",

            "ruta":
                None
        })


    # =====================================================
    # TRIGGERS
    # =====================================================

    for item in metadata.get(
        "triggers",
        []
    ):

        name = item.get(
            "trigger_name",
            ""
        )

        if not name:
            continue

        objetos.append({

            "id":
                name,

            "nombre_objeto":
                name,

            "tipo":
                "Trigger",

            "version":
                None,

            "paquete":
                None,

            "creacion_modificacion":
                "Creacion",

            "herramienta":
                "BASE DE DATOS",

            "ruta":
                None
        })

    return objetos


# =========================================================
# BUILD APEX OBJECTS
# =========================================================

def build_apex_objects(
    apex_files
):

    objetos = []

    for apex_file in apex_files:

        name = safe_stem(
            apex_file.name
        )

        if not name:
            continue

        objetos.append({

            "id":
                name,

            "nombre_objeto":
                name,

            "tipo":
                None,

            "version":
                None,

            "paquete":
                None,

            "creacion_modificacion":
                "Creacion",

            "herramienta":
                "APEX",

            "ruta":
                None
        })

    return objetos


# =========================================================
# POST /api/matriz/register
# =========================================================

@router.post(
    "/matriz/register"
)
async def register_matriz(

    empresa: str = Form(...),

    numero_ticket: str = Form(...),

    objeto_pase: str = Form(...),

    autor: str = Form(...),

    esquema: str = Form(""),

    vb_files:
        Optional[List[UploadFile]]
        =
        File(None),

    apex_files:
        Optional[List[UploadFile]]
        =
        File(None),

    oic_files:
        Optional[List[UploadFile]]
        =
        File(None),

    bip_files:
        Optional[List[UploadFile]]
        =
        File(None),

    sql_files:
        Optional[List[UploadFile]]
        =
        File(None)
):

    try:

        # =====================================================
        # NORMALIZE FORM
        # =====================================================

        empresa = (
            empresa
            .strip()
        )

        numero_ticket = (
            numero_ticket
            .strip()
        )

        objeto_pase = (
            objeto_pase
            .strip()
        )

        autor = (
            autor
            .strip()
        )

        esquema = (
            esquema
            .strip()
        )


        if not empresa:

            return JSONResponse(
                status_code=400,
                content={
                    "status":
                        "ERROR",
                    "mensaje":
                        "Empresa es obligatoria."
                }
            )


        if not numero_ticket:

            return JSONResponse(
                status_code=400,
                content={
                    "status":
                        "ERROR",
                    "mensaje":
                        "Número de ticket es obligatorio."
                }
            )


        if not objeto_pase:

            return JSONResponse(
                status_code=400,
                content={
                    "status":
                        "ERROR",
                    "mensaje":
                        "Nombre de desarrollo es obligatorio."
                }
            )


        if not autor:

            return JSONResponse(
                status_code=400,
                content={
                    "status":
                        "ERROR",
                    "mensaje":
                        "Autor es obligatorio."
                }
            )


        # =====================================================
        # FILES -> MEMORY
        # =====================================================

        vb_memory = (
            await to_memory_files(
                vb_files
            )
        )

        apex_memory = (
            await to_memory_files(
                apex_files
            )
        )

        oic_memory = (
            await to_memory_files(
                oic_files
            )
        )

        bip_memory = (
            await to_memory_files(
                bip_files
            )
        )

        sql_memory = (
            await to_memory_files(
                sql_files
            )
        )


        # =====================================================
        # DATABASE REQUIRES SCHEMA
        # =====================================================

        if (
            sql_memory
            and
            not esquema
        ):

            return JSONResponse(
                status_code=400,
                content={
                    "status":
                        "ERROR",
                    "mensaje":
                        "El esquema es obligatorio cuando se registran objetos de Base de Datos."
                }
            )


        # =====================================================
        # BUILD OBJECTS
        # =====================================================

        objetos = []


        # OIC
        objetos.extend(
            build_oic_objects(
                oic_memory
            )
        )


        # BI PUBLISHER
        objetos.extend(
            build_bip_objects(
                bip_memory
            )
        )


        # VISUAL BUILDER
        objetos.extend(
            build_vb_objects(
                vb_memory
            )
        )


        # DATABASE
        objetos.extend(
            build_database_objects(
                sql_memory
            )
        )


        # APEX
        objetos.extend(
            build_apex_objects(
                apex_memory
            )
        )


        if not objetos:

            return JSONResponse(
                status_code=400,
                content={
                    "status":
                        "ERROR",
                    "mensaje":
                        "No se encontraron objetos para registrar."
                }
            )


        # =====================================================
        # REQUEST ORDS
        # =====================================================

        payload = {

            "empresa":
                empresa,

            "numero_ticket":
                numero_ticket,

            "objeto_pase":
                objeto_pase,

            "autor":
                autor,

            "esquema":
                esquema
                or
                None,

            "objetos":
                objetos
        }


        print(
            "[MATRIZ] ========================================"
        )

        print(
            "[MATRIZ] OBJETOS:",
            len(
                objetos
            )
        )

        print(
            "[MATRIZ] REQUEST:",
            payload
        )

        print(
            "[MATRIZ] ========================================"
        )


        # =====================================================
        # CALL ORDS
        # =====================================================

        async with httpx.AsyncClient(
            timeout=120.0
        ) as client:

            response = await client.post(

                ORDS_MATRIZ_URL,

                json=
                    payload,

                headers={

                    "Content-Type":
                        "application/json",

                    "Accept":
                        "application/json"
                }
            )


        # =====================================================
        # RESPONSE
        # =====================================================

        try:

            response_data = (
                response.json()
            )

        except Exception:

            response_data = {

                "status":
                    "ERROR",

                "mensaje":
                    response.text
                    or
                    "ORDS no devolvió una respuesta JSON."
            }


        print(
            "[MATRIZ] ORDS STATUS:",
            response.status_code
        )

        print(
            "[MATRIZ] ORDS RESPONSE:",
            response_data
        )


        return JSONResponse(

            status_code=
                response.status_code,

            content=
                response_data
        )


    except httpx.TimeoutException as error:

        print(
            "[MATRIZ] TIMEOUT:",
            str(
                error
            )
        )

        return JSONResponse(
            status_code=504,
            content={
                "status":
                    "ERROR",
                "mensaje":
                    "El servicio ORDS excedió el tiempo de espera."
            }
        )


    except httpx.RequestError as error:

        print(
            "[MATRIZ] HTTP ERROR:",
            str(
                error
            )
        )

        return JSONResponse(
            status_code=502,
            content={
                "status":
                    "ERROR",
                "mensaje":
                    (
                        "No fue posible comunicarse "
                        "con el servicio ORDS."
                    )
            }
        )


    except Exception as error:

        print(
            "[MATRIZ] ERROR:",
            repr(
                error
            )
        )

        return JSONResponse(
            status_code=500,
            content={
                "status":
                    "ERROR",
                "mensaje":
                    str(
                        error
                    )
            }
        )
    
# =========================================================
# DOWNLOAD MATRIZ PDF
# =========================================================

@router.get(
    "/matriz/download"
)
async def download_matriz(
    ticket: str = Query(...)
):

    ticket = (
        ticket
        .strip()
    )


    if not ticket:

        return JSONResponse(
            status_code=400,
            content={
                "status":
                    "ERROR",

                "mensaje":
                    "Debe indicar el número de ticket."
            }
        )


    try:

        print(
            "[MATRIZ PDF] Solicitando ticket:",
            ticket
        )


        async with httpx.AsyncClient(
            timeout=120.0
        ) as client:

            response = await client.get(

                ORDS_MATRIZ_PDF_URL,

                params={
                    "ticket":
                        ticket
                },

                headers={
                    "Accept":
                        "application/pdf"
                }
            )


        print(
            "[MATRIZ PDF] ORDS STATUS:",
            response.status_code
        )


        # =================================================
        # ERROR ORDS
        # =================================================

        if response.status_code >= 400:

            content_type = (
                response.headers.get(
                    "content-type",
                    "application/json"
                )
            )


            return Response(

                content=
                    response.content,

                status_code=
                    response.status_code,

                media_type=
                    content_type
            )


        # =================================================
        # PDF
        # =================================================

        content_disposition = (
            response.headers.get(
                "content-disposition"
            )
            or
            (
                'attachment; filename="'
                'NEO-GD-RG-03 Inventario de Objetos de Desarrollo.pdf'
                '"'
            )
        )


        return Response(

            content=
                response.content,

            status_code=
                200,

            media_type=
                "application/pdf",

            headers={
                "Content-Disposition":
                    content_disposition,

                "Cache-Control":
                    "no-store"
            }
        )


    except httpx.TimeoutException:

        return JSONResponse(
            status_code=504,
            content={
                "status":
                    "ERROR",

                "mensaje":
                    "AOP excedió el tiempo de espera generando el PDF."
            }
        )


    except httpx.RequestError as error:

        print(
            "[MATRIZ PDF] Error HTTP:",
            str(error)
        )


        return JSONResponse(
            status_code=502,
            content={
                "status":
                    "ERROR",

                "mensaje":
                    "No fue posible comunicarse con el servicio de descarga."
            }
        )


    except Exception as error:

        print(
            "[MATRIZ PDF] ERROR:",
            repr(error)
        )


        return JSONResponse(
            status_code=500,
            content={
                "status":
                    "ERROR",

                "mensaje":
                    str(error)
            }
        )
    
# =========================================================
# DOWNLOAD MATRIZ PDF
# =========================================================

@router.get(
    "/matriz/download"
)
async def download_matriz(
    ticket: str = Query(...)
):

    ticket = ticket.strip()


    if not ticket:

        return JSONResponse(
            status_code=400,
            content={
                "status": "ERROR",
                "mensaje":
                    "Debe indicar el número de ticket."
            }
        )


    try:

        print(
            "[MATRIZ PDF] Ticket:",
            ticket
        )


        async with httpx.AsyncClient(
            timeout=120.0
        ) as client:

            response = await client.get(

                ORDS_MATRIZ_PDF_URL,

                params={
                    "ticket":
                        ticket
                },

                headers={
                    "Accept":
                        "application/pdf"
                }
            )


        print(
            "[MATRIZ PDF] ORDS STATUS:",
            response.status_code
        )


        # =================================================
        # ERROR ORDS
        # =================================================

        if response.status_code >= 400:

            content_type = (
                response.headers.get(
                    "content-type",
                    "application/json"
                )
            )

            return Response(

                content=
                    response.content,

                status_code=
                    response.status_code,

                media_type=
                    content_type
            )


        # =================================================
        # PDF
        # =================================================

        content_disposition = (
            response.headers.get(
                "content-disposition"
            )
            or
            (
                'attachment; filename="'
                'NEO-GD-RG-03 Inventario de Objetos de Desarrollo.pdf'
                '"'
            )
        )


        return Response(

            content=
                response.content,

            status_code=
                200,

            media_type=
                "application/pdf",

            headers={

                "Content-Disposition":
                    content_disposition,

                "Cache-Control":
                    "no-store"
            }
        )


    except httpx.TimeoutException:

        return JSONResponse(
            status_code=504,
            content={
                "status": "ERROR",
                "mensaje":
                    "AOP excedió el tiempo de espera generando el PDF."
            }
        )


    except httpx.RequestError as error:

        print(
            "[MATRIZ PDF] HTTP ERROR:",
            str(error)
        )

        return JSONResponse(
            status_code=502,
            content={
                "status": "ERROR",
                "mensaje":
                    "No fue posible comunicarse con ORDS."
            }
        )


    except Exception as error:

        print(
            "[MATRIZ PDF] ERROR:",
            repr(error)
        )

        return JSONResponse(
            status_code=500,
            content={
                "status": "ERROR",
                "mensaje":
                    str(error)
            }
        )