# =========================================================
# FILE:
# oic_doc_generator/backend/utils/toc_updater.py
# =========================================================

from pathlib import Path

import os
import shutil
import subprocess


# =========================================================
# FIND SYSTEM PYTHON
# =========================================================

def _find_system_python():

    candidates = [

        "/usr/bin/python3",

        "/usr/local/bin/python3"
    ]


    for path in candidates:

        if os.path.exists(
            path
        ):

            return path


    python_path = shutil.which(
        "python3"
    )


    if python_path:

        return python_path


    raise RuntimeError(
        "No se encontró Python del sistema."
    )


# =========================================================
# UPDATE TABLE OF CONTENTS
# =========================================================

def update_table_of_contents(
    docx_path,
    output_path=None,
    timeout=45
):

    source_path = Path(
        docx_path
    ).resolve()


    if not source_path.exists():

        raise FileNotFoundError(
            f"No existe el documento: {source_path}"
        )


    # =====================================================
    # OUTPUT
    # =====================================================

    if output_path:

        target_path = Path(
            output_path
        ).resolve()


        target_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )


        shutil.copy2(
            source_path,
            target_path
        )

    else:

        target_path = (
            source_path
        )


    # =====================================================
    # SYSTEM PYTHON
    # =====================================================

    system_python = (
        _find_system_python()
    )


    # =====================================================
    # WORKER PATH
    # =====================================================

    worker_path = (

        Path(
            __file__
        )
        .resolve()
        .parent
        /
        "toc_uno_worker.py"
    )


    if not worker_path.exists():

        raise RuntimeError(
            f"No existe el worker UNO: {worker_path}"
        )


    print(
        "[TOC] Python aplicación:",
        os.sys.executable
    )


    print(
        "[TOC] Python UNO:",
        system_python
    )


    print(
        "[TOC] Ejecutando worker..."
    )


    # =====================================================
    # EXECUTE SYSTEM PYTHON
    # =====================================================

    result = subprocess.run(

        [
            system_python,

            str(
                worker_path
            ),

            str(
                target_path
            ),

            str(
                timeout
            )
        ],

        stdout=subprocess.PIPE,

        stderr=subprocess.PIPE,

        text=True,

        timeout=
            timeout + 30
    )


    # =====================================================
    # LOG
    # =====================================================

    if result.stdout:

        print(
            result.stdout
        )


    if result.stderr:

        print(
            "[TOC STDERR]"
        )

        print(
            result.stderr
        )


    # =====================================================
    # VALIDATE
    # =====================================================

    if result.returncode != 0:

        raise RuntimeError(

            "No fue posible actualizar la tabla "
            "de contenido con LibreOffice. "
            f"Exit code: {result.returncode}. "
            f"STDOUT: {result.stdout}. "
            f"STDERR: {result.stderr}"
        )


    print(
        "[TOC] Proceso finalizado correctamente."
    )


    return str(
        target_path
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