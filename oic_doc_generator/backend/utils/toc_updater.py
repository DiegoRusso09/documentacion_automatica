# =========================================================
# FILE:
# oic_doc_generator/backend/utils/toc_updater.py
# =========================================================

from pathlib import Path

import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time


# =========================================================
# UNO IMPORT
# =========================================================

def _import_uno():
    """
    Importa el módulo UNO utilizado por LibreOffice.

    En servidores Linux/Debian, python3-uno normalmente se
    instala dentro de /usr/lib/python3/dist-packages, ruta
    que puede no estar visible desde un virtualenv.
    """

    try:

        import uno

        return uno

    except ImportError:

        possible_paths = [

            "/usr/lib/python3/dist-packages",

            "/usr/lib/libreoffice/program",

            "/usr/lib64/libreoffice/program"
        ]


        for path in possible_paths:

            if (
                os.path.exists(path)
                and
                path not in sys.path
            ):

                sys.path.append(
                    path
                )


        try:

            import uno

            return uno

        except ImportError as error:

            raise RuntimeError(
                "No se pudo importar el módulo 'uno'. "
                "Instale LibreOffice y python3-uno."
            ) from error


# =========================================================
# FIND LIBREOFFICE
# =========================================================

def _find_libreoffice():

    candidates = [

        "libreoffice",

        "soffice"
    ]


    for executable in candidates:

        path = shutil.which(
            executable
        )


        if path:

            return path


    possible_paths = [

        "/usr/bin/libreoffice",

        "/usr/bin/soffice",

        "/usr/lib/libreoffice/program/soffice"
    ]


    for path in possible_paths:

        if os.path.exists(
            path
        ):

            return path


    raise RuntimeError(
        "LibreOffice no está instalado "
        "o no se encontró el ejecutable."
    )


# =========================================================
# FREE PORT
# =========================================================

def _get_free_port():

    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    ) as sock:

        sock.bind(
            (
                "127.0.0.1",
                0
            )
        )


        return (
            sock
            .getsockname()[1]
        )


# =========================================================
# PROPERTY
# =========================================================

def _create_property(
    uno,
    name,
    value
):

    prop = uno.createUnoStruct(
        "com.sun.star.beans.PropertyValue"
    )


    prop.Name = (
        name
    )


    prop.Value = (
        value
    )


    return prop


# =========================================================
# START LIBREOFFICE
# =========================================================

def _start_libreoffice(
    port,
    profile_dir
):

    executable = (
        _find_libreoffice()
    )


    profile_url = (
        Path(profile_dir)
        .resolve()
        .as_uri()
    )


    command = [

        executable,

        "--headless",

        "--nologo",

        "--nodefault",

        "--nofirststartwizard",

        "--norestore",

        "--nolockcheck",

        (
            "-env:UserInstallation="
            f"{profile_url}"
        ),

        (
            "--accept="
            f"socket,host=127.0.0.1,port={port};"
            "urp;"
            "StarOffice.ComponentContext"
        )
    ]


    print(
        "[TOC] Iniciando LibreOffice..."
    )


    process = subprocess.Popen(

        command,

        stdout=subprocess.PIPE,

        stderr=subprocess.PIPE,

        text=True
    )


    return process


# =========================================================
# CONNECT UNO
# =========================================================

def _connect_to_libreoffice(
    uno,
    port,
    timeout=30
):

    local_context = (
        uno.getComponentContext()
    )


    resolver = (
        local_context
        .ServiceManager
        .createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver",
            local_context
        )
    )


    connection_string = (

        f"uno:socket,"
        f"host=127.0.0.1,"
        f"port={port};"
        f"urp;"
        f"StarOffice.ComponentContext"
    )


    started = time.time()

    last_error = None


    while (
        time.time()
        -
        started
        <
        timeout
    ):

        try:

            context = resolver.resolve(
                connection_string
            )


            print(
                "[TOC] Conexión UNO establecida."
            )


            return context

        except Exception as error:

            last_error = error

            time.sleep(
                0.5
            )


    raise RuntimeError(
        "No fue posible conectarse con LibreOffice "
        f"después de {timeout} segundos. "
        f"Último error: {last_error}"
    )


# =========================================================
# REFRESH DOCUMENT INDEXES
# =========================================================

def _refresh_document_indexes(
    document
):

    print(
        "[TOC] Actualizando tabla de contenido..."
    )


    # =====================================================
    # DOCUMENT INDEXES
    # =====================================================
    #
    # Aquí se encuentran:
    #
    # - Tabla de contenido
    # - Índices
    # - Otros DocumentIndexes
    #
    # =====================================================

    indexes = (
        document.getDocumentIndexes()
    )


    total_indexes = (
        indexes.getCount()
    )


    print(
        f"[TOC] Índices encontrados: {total_indexes}"
    )


    for index_number in range(
        total_indexes
    ):

        index = indexes.getByIndex(
            index_number
        )


        try:

            index.update()


            print(
                "[TOC] Índice actualizado:",
                index_number + 1
            )

        except Exception as error:

            print(
                "[TOC] No se pudo actualizar índice",
                index_number + 1,
                ":",
                error
            )


    # =====================================================
    # TEXT FIELDS
    # =====================================================

    try:

        text_fields = (
            document.getTextFields()
        )


        text_fields.refresh()


        print(
            "[TOC] Campos de texto actualizados."
        )

    except Exception as error:

        print(
            "[TOC] No fue posible refrescar "
            "todos los campos:",
            error
        )


# =========================================================
# UPDATE TABLE OF CONTENTS
# =========================================================

def update_table_of_contents(
    docx_path,
    output_path=None,
    timeout=30
):
    """
    Abre un DOCX con LibreOffice Headless,
    actualiza la tabla de contenido y guarda
    nuevamente el documento.

    Parameters
    ----------
    docx_path:
        Ruta del archivo DOCX generado.

    output_path:
        Ruta destino.

        Si no se especifica, se actualiza
        el mismo archivo.

    timeout:
        Tiempo máximo de espera para conectar
        con LibreOffice.

    Returns
    -------
    str
        Ruta absoluta del DOCX actualizado.
    """

    uno = (
        _import_uno()
    )


    source_path = Path(
        docx_path
    ).resolve()


    if not source_path.exists():

        raise FileNotFoundError(
            f"No existe el documento: {source_path}"
        )


    if (
        source_path.suffix.lower()
        !=
        ".docx"
    ):

        raise ValueError(
            "El archivo debe tener extensión .docx"
        )


    # =====================================================
    # OUTPUT PATH
    # =====================================================

    if output_path:

        destination_path = Path(
            output_path
        ).resolve()

    else:

        destination_path = (
            source_path
        )


    destination_path.parent.mkdir(

        parents=True,

        exist_ok=True
    )


    # =====================================================
    # TEMP LIBREOFFICE PROFILE
    # =====================================================

    profile_dir = tempfile.mkdtemp(
        prefix="ds140_lo_profile_"
    )


    port = (
        _get_free_port()
    )


    libreoffice_process = None

    document = None


    try:

        # =================================================
        # START LIBREOFFICE
        # =================================================

        libreoffice_process = (
            _start_libreoffice(

                port,

                profile_dir
            )
        )


        # =================================================
        # CONNECT
        # =================================================

        context = (
            _connect_to_libreoffice(

                uno,

                port,

                timeout
            )
        )


        service_manager = (
            context.ServiceManager
        )


        desktop = (
            service_manager
            .createInstanceWithContext(

                "com.sun.star.frame.Desktop",

                context
            )
        )


        # =================================================
        # OPEN DOCUMENT
        # =================================================

        source_url = (
            uno.systemPathToFileUrl(
                str(
                    source_path
                )
            )
        )


        load_properties = (

            _create_property(
                uno,
                "Hidden",
                True
            ),

            _create_property(
                uno,
                "ReadOnly",
                False
            )
        )


        print(
            "[TOC] Abriendo documento:",
            source_path
        )


        document = (
            desktop.loadComponentFromURL(

                source_url,

                "_blank",

                0,

                load_properties
            )
        )


        if document is None:

            raise RuntimeError(
                "LibreOffice no pudo abrir el documento."
            )


        # =================================================
        # WAIT FOR DOCUMENT
        # =================================================

        time.sleep(
            1
        )


        # =================================================
        # REFRESH TOC
        # =================================================

        _refresh_document_indexes(
            document
        )


        # =================================================
        # WAIT FOR PAGINATION
        # =================================================
        #
        # LibreOffice necesita un pequeño tiempo para
        # recalcular los números de página después de
        # actualizar el índice.
        #
        # =================================================

        time.sleep(
            1
        )


        # =================================================
        # SAVE
        # =================================================

        if (
            destination_path
            ==
            source_path
        ):

            print(
                "[TOC] Guardando documento actualizado..."
            )


            document.store()

        else:

            destination_url = (
                uno.systemPathToFileUrl(
                    str(
                        destination_path
                    )
                )
            )


            save_properties = (

                _create_property(
                    uno,
                    "FilterName",
                    "Office Open XML Text"
                ),

                _create_property(
                    uno,
                    "Overwrite",
                    True
                )
            )


            print(
                "[TOC] Guardando documento en:",
                destination_path
            )


            document.storeAsURL(

                destination_url,

                save_properties
            )


        print(
            "[TOC] Tabla de contenido actualizada correctamente."
        )


        return str(
            destination_path
        )


    finally:

        # =================================================
        # CLOSE DOCUMENT
        # =================================================

        if document is not None:

            try:

                document.close(
                    True
                )

            except Exception:

                try:

                    document.dispose()

                except Exception:

                    pass


        # =================================================
        # STOP LIBREOFFICE
        # =================================================

        if libreoffice_process is not None:

            try:

                libreoffice_process.terminate()


                libreoffice_process.wait(
                    timeout=5
                )

            except Exception:

                try:

                    libreoffice_process.kill()

                except Exception:

                    pass


        # =================================================
        # CLEAN PROFILE
        # =================================================

        shutil.rmtree(

            profile_dir,

            ignore_errors=True
        )


# =========================================================
# ALIAS
# =========================================================

def update_toc(
    docx_path,
    output_path=None
):

    return update_table_of_contents(

        docx_path,

        output_path
    )


# =========================================================
# CLI TEST
# =========================================================

if __name__ == "__main__":

    if len(
        sys.argv
    ) < 2:

        print(
            "Uso:"
        )

        print(
            "python toc_updater.py documento.docx"
        )

        sys.exit(
            1
        )


    input_document = (
        sys.argv[
            1
        ]
    )


    if (
        len(
            sys.argv
        )
        >=
        3
    ):

        output_document = (
            sys.argv[
                2
            ]
        )

    else:

        output_document = None


    result = (
        update_table_of_contents(

            input_document,

            output_document
        )
    )


    print(
        "[TOC] Documento final:",
        result
    )