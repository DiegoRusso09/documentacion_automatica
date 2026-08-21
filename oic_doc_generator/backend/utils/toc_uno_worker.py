# =========================================================
# FILE:
# oic_doc_generator/backend/utils/toc_uno_worker.py
# =========================================================

from pathlib import Path

import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time


try:

    import uno

except ImportError as error:

    print(
        "[TOC WORKER] No se pudo importar UNO:",
        error
    )

    sys.exit(
        2
    )


# =========================================================
# FIND LIBREOFFICE
# =========================================================

def find_libreoffice():

    for executable in [
        "libreoffice",
        "soffice"
    ]:

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
        "No se encontró LibreOffice."
    )


# =========================================================
# FREE PORT
# =========================================================

def get_free_port():

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

        return sock.getsockname()[1]


# =========================================================
# UNO PROPERTY
# =========================================================

def create_property(
    name,
    value
):

    prop = uno.createUnoStruct(
        "com.sun.star.beans.PropertyValue"
    )

    prop.Name = name

    prop.Value = value

    return prop


# =========================================================
# CONNECT
# =========================================================

def connect_to_libreoffice(
    port,
    timeout
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


    start_time = time.time()

    last_error = None


    while (
        time.time() - start_time
        <
        timeout
    ):

        try:

            return resolver.resolve(
                connection_string
            )

        except Exception as error:

            last_error = error

            time.sleep(
                0.5
            )


    raise RuntimeError(
        "No se pudo conectar con LibreOffice. "
        f"Último error: {last_error}"
    )


# =========================================================
# UPDATE TOC
# =========================================================

def update_toc(
    docx_path,
    timeout=45
):

    source_path = Path(
        docx_path
    ).resolve()


    if not source_path.exists():

        raise FileNotFoundError(
            f"No existe: {source_path}"
        )


    libreoffice = (
        find_libreoffice()
    )


    profile_dir = tempfile.mkdtemp(
        prefix="ds140_lo_"
    )


    profile_url = (
        Path(profile_dir)
        .resolve()
        .as_uri()
    )


    port = (
        get_free_port()
    )


    process = None

    document = None


    try:

        # =================================================
        # START LIBREOFFICE
        # =================================================

        command = [

            libreoffice,

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
            "[TOC WORKER] Iniciando LibreOffice..."
        )


        process = subprocess.Popen(

            command,

            stdout=subprocess.DEVNULL,

            stderr=subprocess.PIPE,

            text=True
        )


        # =================================================
        # CONNECT
        # =================================================

        context = connect_to_libreoffice(
            port,
            timeout
        )


        print(
            "[TOC WORKER] Conexión UNO establecida."
        )


        desktop = (
            context
            .ServiceManager
            .createInstanceWithContext(
                "com.sun.star.frame.Desktop",
                context
            )
        )


        # =================================================
        # OPEN DOCX
        # =================================================

        source_url = (
            uno.systemPathToFileUrl(
                str(
                    source_path
                )
            )
        )


        properties = (

            create_property(
                "Hidden",
                True
            ),

            create_property(
                "ReadOnly",
                False
            )
        )


        print(
            "[TOC WORKER] Abriendo:",
            source_path
        )


        document = (
            desktop.loadComponentFromURL(

                source_url,

                "_blank",

                0,

                properties
            )
        )


        if document is None:

            raise RuntimeError(
                "LibreOffice no pudo abrir el DOCX."
            )


        # Da tiempo a Writer a calcular layout/páginas
        time.sleep(
            1
        )


        # =================================================
        # UPDATE INDEXES
        # =================================================

        indexes = (
            document.getDocumentIndexes()
        )


        count = (
            indexes.getCount()
        )


        print(
            f"[TOC WORKER] Índices encontrados: {count}"
        )


        for index_number in range(
            count
        ):

            index = indexes.getByIndex(
                index_number
            )


            index.update()


            print(
                "[TOC WORKER] Índice actualizado:",
                index_number + 1
            )


        # =================================================
        # UPDATE TEXT FIELDS
        # =================================================

        try:

            document
            .getTextFields()
            .refresh()

            print(
                "[TOC WORKER] Campos actualizados."
            )

        except Exception as error:

            print(
                "[TOC WORKER] Aviso al refrescar campos:",
                error
            )


        # =================================================
        # PAGINATION
        # =================================================

        time.sleep(
            2
        )


        # =================================================
        # SAVE
        # =================================================

        document.store()


        print(
            "[TOC WORKER] Documento guardado."
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

        if process is not None:

            try:

                process.terminate()

                process.wait(
                    timeout=5
                )

            except Exception:

                try:

                    process.kill()

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
# MAIN
# =========================================================

def main():

    if len(
        sys.argv
    ) < 2:

        print(
            "Uso: toc_uno_worker.py archivo.docx"
        )

        return 1


    docx_path = (
        sys.argv[
            1
        ]
    )


    if len(
        sys.argv
    ) >= 3:

        timeout = int(
            sys.argv[
                2
            ]
        )

    else:

        timeout = 45


    try:

        update_toc(
            docx_path,
            timeout
        )

        return 0

    except Exception as error:

        print(
            "[TOC WORKER ERROR]",
            repr(
                error
            )
        )

        return 1


if __name__ == "__main__":

    sys.exit(
        main()
    )