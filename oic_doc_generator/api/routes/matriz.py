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

from oic_doc_generator.backend.parsers.project_parser import (
    get_project_name,
    get_project_version
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
# OIC ID
# =========================================================

def infer_oic_id(
    iar_path: str,
    integration_name: str
):

    file_name = os.path.basename(
        iar_path
    )

    stem = Path(
        file_name
    ).stem

    # Oracle puede exportar IAR con prefijos como IC_
    stem = re.sub(
        r"^(IC_|IAR_)",
        "",
        stem,
        flags=re.IGNORECASE
    )

    # Remueve versiones al final:
    # _01.00.0000
    # _1.0.2
    stem = re.sub(
        r"[_-]\d+(?:\.\d+){1,3}$",
        "",
        stem
    )

    stem = stem.strip(
        "_- "
    )

    if stem:
        return stem

    return integration_name


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
            # IAR
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

            # =================================================
            # PROCESS IAR
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

                try:

                    integration_name = (
                        get_project_name(
                            extracted_iar
                        )
                    )

                except Exception:

                    integration_name = None

                if not integration_name:

                    integration_name = (
                        safe_stem(
                            os.path.basename(
                                iar_path
                            )
                        )
                    )

                try:

                    version = (
                        get_project_version(
                            extracted_iar
                        )
                    )

                except Exception:

                    version = None

                try:

                    scheduled = (
                        is_scheduled_integration(
                            extracted_iar
                        )
                    )

                except Exception:

                    scheduled = False

                integration_id = (
                    infer_oic_id(
                        iar_path,
                        integration_name
                    )
                )

                package_name = (
                    extract_oic_package_name(
                        extracted_iar
                    )
                )

                integration_type = (
                    "Integración Programada"
                    if scheduled
                    else
                    "Integración REST"
                )

                objetos.append({

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
                })

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

    for bip_file in bip_files:

        extension = (
            Path(
                bip_file.name
            )
            .suffix
            .lower()
        )

        name = safe_stem(
            bip_file.name
        )

        if not name:
            continue

        if extension == ".xdmz":

            object_type = (
                "Data Model"
            )

        elif extension in [
            ".xdoz",
            ".xdrz"
        ]:

            object_type = (
                "Report"
            )

        else:

            continue

        objetos.append({

            "id":
                name,

            "nombre_objeto":
                name,

            "tipo":
                object_type,

            "version":
                None,

            "paquete":
                None,

            "creacion_modificacion":
                "Creacion",

            "herramienta":
                "BI Publisher",

            "ruta":
                None
        })

    return objetos


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