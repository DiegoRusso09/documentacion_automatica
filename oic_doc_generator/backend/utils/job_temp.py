# =========================================================
# FILE: job_temp.py
# =========================================================
#
# Temporales por trabajo (DS140 / IM090).
#
# Cada generación extrae el .par, cada .iar, los BIP, las
# apps VB, imágenes... con tempfile.mkdtemp en muchos sitios
# del código, y casi nada se borraba: el disco se llenaba.
#
# job_temp_dir() hace que TODO lo que se cree con
# tempfile.mkdtemp / tempfile.mkstemp (sin "dir" explícito)
# dentro del hilo del trabajo vaya a una carpeta propia, que
# se borra entera al terminar, aunque el trabajo falle.
#
# El resultado que se descarga después (el ZIP de entrega)
# se crea fuera, con dir=tempfile.gettempdir(); las entregas
# viejas se borran con clean_old_deliveries().
# =========================================================

import os
import shutil
import tempfile
import threading
import time

from contextlib import contextmanager


_local = threading.local()

_original_mkdtemp = tempfile.mkdtemp

_original_mkstemp = tempfile.mkstemp

DELIVERY_PREFIXES = (
    "ds140_delivery_",
    "im090_delivery_",
    "oic_delivery_"
)


def _job_dir(directory):

    root = getattr(_local, "root", None)

    if directory is None and root:
        return root

    return directory


def _mkdtemp(suffix=None, prefix=None, dir=None):

    return _original_mkdtemp(suffix, prefix, _job_dir(dir))


def _mkstemp(suffix=None, prefix=None, dir=None, text=False):

    return _original_mkstemp(suffix, prefix, _job_dir(dir), text)


# Se instala una sola vez; fuera de un trabajo se comporta
# igual que tempfile original.
if tempfile.mkdtemp is not _mkdtemp:

    tempfile.mkdtemp = _mkdtemp

    tempfile.mkstemp = _mkstemp


@contextmanager
def job_temp_dir(label):

    root = _original_mkdtemp(prefix=f"{label}_job_")

    previous = getattr(_local, "root", None)

    _local.root = root

    try:

        yield root

    finally:

        _local.root = previous

        shutil.rmtree(root, ignore_errors=True)

        print(f"[TEMP] Temporales del trabajo borrados: {root}")


def clean_old_deliveries(max_age_hours=2):

    # Borra entregas (ZIP) viejas que ya no se van a descargar.
    base = tempfile.gettempdir()

    limit = time.time() - max_age_hours * 3600

    removed = 0

    try:
        names = os.listdir(base)
    except OSError:
        return 0

    for name in names:

        if not name.startswith(DELIVERY_PREFIXES):
            continue

        path = os.path.join(base, name)

        try:

            if os.path.isdir(path) and os.path.getmtime(path) < limit:

                shutil.rmtree(path, ignore_errors=True)

                removed += 1

        except OSError:
            continue

    if removed:
        print(f"[TEMP] Entregas antiguas borradas: {removed}")

    return removed
