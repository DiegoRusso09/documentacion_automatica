# =========================================================
# FILE:
# oic_doc_generator/api/services/ai_providers.py
# =========================================================
#
# Cadena de proveedores de IA compatibles con la API de OpenAI.
#
# Se usa el primer proveedor disponible; si alcanza su tope
# diario, devuelve límite de peticiones o falla, se pasa al
# siguiente. Si todos fallan, el llamador usa el esquema
# determinístico.
#
# CONFIGURACIÓN (primer archivo que exista):
#   1. Ruta en la variable de entorno AI_PROVIDERS_FILE
#   2. /etc/secrets/ia_proveedores.json   (Secret File de Render)
#   3. ia_proveedores.json en la raíz del proyecto
#
# Sin archivo: se usa GEMINI_API_KEY u OPENAI_API_KEY.
# En el archivo, una api_key vacía se toma de <NOMBRE>_API_KEY.
#
# Solo se admite UNA entrada por proveedor. Cada entrada puede
# tener "claves_respaldo": claves de OTROS proyectos de Google
# (el cupo de Gemini es por proyecto, no por clave). Se usan
# cuando la clave activa agota su cupo diario, llega al límite
# por minuto o deja de ser válida; así se suman los cupos.
# =========================================================

import json
import os
import re
import tempfile
import threading
import time

from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    OpenAI,
    PermissionDeniedError,
    RateLimitError
)


# =========================================================
# KNOWN PROVIDERS
# =========================================================

KNOWN_PROVIDERS = {

    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "modelo": "gemini-3.5-flash-lite"
    },

    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "modelo": "openai/gpt-oss-120b"
    },

    "cerebras": {
        "base_url": "https://api.cerebras.ai/v1",
        "modelo": "gpt-oss-120b"
    },

    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "modelo": None
    },

    "mistral": {
        "base_url": "https://api.mistral.ai/v1",
        "modelo": "mistral-small-latest"
    },

    "openai": {
        "base_url": None,
        "modelo": "gpt-5.6-luna"
    }
}


PROJECT_ROOT = Path(__file__).resolve().parents[3]

CONFIG_LOCATIONS = [
    os.getenv("AI_PROVIDERS_FILE", ""),
    "/etc/secrets/ia_proveedores.json",
    str(PROJECT_ROOT / "ia_proveedores.json")
]

USAGE_FILE = os.path.join(
    tempfile.gettempdir(),
    "ds140_ia_uso.json"
)

TIMEOUT_SECONDS = float(
    os.getenv(
        "AI_TIMEOUT_SECONDS",
        "90"
    )
)

# Espera máxima cuando todos los proveedores están en límite
# por minuto (planes gratuitos).
RATE_LIMIT_MAX_WAIT = 65

# Pausa para un proveedor que falló por un motivo distinto
# del límite (caída, timeout, clave inválida, modelo inexistente).
ERROR_COOLDOWN_SECONDS = 300


_lock = threading.Lock()

_cooldown_until = {}


# =========================================================
# CONFIG
# =========================================================

def _load_entries():

    for location in CONFIG_LOCATIONS:

        if location and os.path.isfile(location):

            with open(location, encoding="utf-8") as file:

                data = json.load(file)

            print(f"[AI] Proveedores leídos de {location}")

            return data.get("proveedores", [])

    # Compatibilidad: variables de entorno de un solo proveedor.
    # GEMINI_API_KEY y OPENAI_API_KEY aceptan varias claves separadas
    # por comas; la primera es la principal y el resto van a
    # claves_respaldo para failover automático si una se agota.
    entries = []

    gemini_keys = [
        k.strip()
        for k in (os.getenv("GEMINI_API_KEY") or "").split(",")
        if k.strip()
    ]

    if gemini_keys:

        entries.append({
            "nombre": "gemini",
            "api_key": gemini_keys[0],
            "modelo": os.getenv("AI_MODEL"),
            "claves_respaldo": gemini_keys[1:]
        })

    elif os.getenv("OPENAI_API_KEY"):

        openai_keys = [
            k.strip()
            for k in (os.getenv("OPENAI_API_KEY") or "").split(",")
            if k.strip()
        ]

        entries.append({
            "nombre": "openai",
            "api_key": openai_keys[0],
            "modelo": os.getenv("AI_MODEL") or os.getenv("OPENAI_TEXT_MODEL"),
            "claves_respaldo": openai_keys[1:]
        })

    return entries


def _build_providers():

    providers = []

    seen_names = set()

    seen_hosts = set()

    for entry in _load_entries():

        name = (entry.get("nombre") or "").strip().lower()

        # Clave vacía en el archivo: se busca en <NOMBRE>_API_KEY
        # (por ejemplo GEMINI_API_KEY o GROQ_API_KEY).
        api_key = (
            entry.get("api_key")
            or os.getenv(f"{name.upper()}_API_KEY", "")
        ).strip()

        if not name or not api_key or entry.get("activo") is False:
            continue

        known = KNOWN_PROVIDERS.get(name, {})

        base_url = entry.get("base_url") or known.get("base_url")

        model = entry.get("modelo") or known.get("modelo")

        if not model:

            print(f"[AI] {name}: falta 'modelo'; proveedor omitido.")

            continue

        if name not in KNOWN_PROVIDERS and not base_url:

            print(f"[AI] {name}: falta 'base_url'; proveedor omitido.")

            continue

        host = urlparse(base_url or "https://api.openai.com").hostname

        # Una entrada por proveedor (por nombre y por servidor).
        if name in seen_names or host in seen_hosts:

            print(
                f"[AI] {name}: ya hay una entrada para ese proveedor; "
                f"se ignora esta (usa claves_respaldo para más claves)."
            )

            continue

        seen_names.add(name)

        seen_hosts.add(host)

        # Claves de respaldo: sustituyen a la principal si se agota
        # (límite de peticiones, cupo diario) o deja de ser válida.
        keys = [api_key] + [
            key.strip()
            for key in entry.get("claves_respaldo") or []
            if key and key.strip()
        ]

        clients = [
            OpenAI(
                api_key=key,
                base_url=base_url,
                timeout=TIMEOUT_SECONDS,
                # Sin reintentos internos: ante un fallo se pasa
                # directamente al siguiente proveedor.
                max_retries=0
            )
            for key in keys
        ]

        providers.append({
            "nombre": name,
            "modelo": model,
            "tope_diario": int(entry.get("tope_diario") or 0),
            "clients": clients,
            "client": clients[0],
            "clave_activa": 0
        })

    return providers


PROVIDERS = _build_providers()


def is_enabled():

    return bool(PROVIDERS)


def describe():

    if not PROVIDERS:
        return "desactivada"

    return " → ".join(
        f"{p['nombre']}/{p['modelo']}"
        for p in PROVIDERS
    )


# =========================================================
# DAILY USAGE
# =========================================================
#
# El cupo diario de Gemini se reinicia a medianoche del
# Pacífico (America/Los_Angeles, con horario de verano).
#
# Cada clave pertenece a un proyecto distinto y tiene su
# propio cupo, así que el uso se lleva por clave:
#
#   {"<fecha>": {"gemini#0": 12, "gemini#1": 3,
#                "_agotadas": ["gemini#0"]}}
#
# "_agotadas" guarda las claves a las que Gemini ya respondió
# que el cupo del día se acabó, para no volver a probarlas
# hasta el reinicio.
# =========================================================

def _pacific_now():

    # Horario de verano de EE. UU.: del segundo domingo de marzo
    # al primer domingo de noviembre, a las 2:00 hora local.
    # (Sin zoneinfo: en Windows requiere el paquete tzdata.)
    now_utc = datetime.now(timezone.utc)

    year = now_utc.year

    march_1 = datetime(year, 3, 1, tzinfo=timezone.utc)

    november_1 = datetime(year, 11, 1, tzinfo=timezone.utc)

    dst_start = march_1 + timedelta(
        days=(6 - march_1.weekday()) % 7 + 7,
        hours=2 + 8
    )

    dst_end = november_1 + timedelta(
        days=(6 - november_1.weekday()) % 7,
        hours=2 + 7
    )

    offset = 7 if dst_start <= now_utc < dst_end else 8

    return now_utc - timedelta(hours=offset)


def _today():

    return _pacific_now().strftime("%Y-%m-%d")


def _key_id(provider, key_idx):

    return f"{provider['nombre']}#{key_idx}"


def _read_usage():

    try:

        with open(USAGE_FILE, encoding="utf-8") as file:
            usage = json.load(file)

    except (OSError, ValueError):

        usage = {}

    return usage.get(_today(), {})


def _write_usage(today_usage):

    # Solo se conserva el día actual.
    with open(USAGE_FILE, "w", encoding="utf-8") as file:
        json.dump({_today(): today_usage}, file)


def _reserve_request(provider, key_idx):

    # Cuenta la petición antes de enviarla; devuelve False si la
    # clave ya agotó su cupo del día (según Gemini o según
    # tope_diario).
    key_id = _key_id(provider, key_idx)

    with _lock:

        today_usage = _read_usage()

        if key_id in today_usage.get("_agotadas", []):
            return False

        used = today_usage.get(key_id, 0)

        if provider["tope_diario"] and used >= provider["tope_diario"]:
            return False

        today_usage[key_id] = used + 1

        _write_usage(today_usage)

        return True


def _mark_exhausted(provider, key_idx):

    key_id = _key_id(provider, key_idx)

    with _lock:

        today_usage = _read_usage()

        exhausted = today_usage.setdefault("_agotadas", [])

        if key_id not in exhausted:
            exhausted.append(key_id)

        _write_usage(today_usage)


def usage_today():

    totals = {}

    for key, count in _read_usage().items():

        if key.startswith("_") or "#" not in key:
            continue

        provider = key.split("#")[0]

        totals[provider] = totals.get(provider, 0) + count

    return totals


def exhausted_keys_today():

    return list(_read_usage().get("_agotadas", []))


# =========================================================
# ERRORS
# =========================================================
#
# Gemini responde 429 RESOURCE_EXHAUSTED con un detalle
# google.rpc.QuotaFailure cuyo quotaId indica la ventana:
#
#   GenerateRequestsPerDayPerProjectPerModel-FreeTier     (día)
#   GenerateRequestsPerMinutePerProjectPerModel-FreeTier  (minuto)
#   GenerateContentInputTokensPerModelPerMinute-FreeTier  (tokens/min)
#
# y quotaValue con el límite real del proyecto. El retryDelay
# de RetryInfo NO sirve para distinguirlos: en el diario
# también trae unos pocos segundos.
# =========================================================

def _error_text(error):

    body = getattr(error, "body", None)

    try:
        body_text = json.dumps(body)
    except (TypeError, ValueError):
        body_text = str(body)

    return f"{error} {body_text}"


def _is_daily_quota_error(error):

    return "PerDay" in _error_text(error)


def _quota_value(error):

    match = re.search(
        r"quotaValue\W+(\d+)",
        _error_text(error)
    )

    return match.group(1) if match else "?"


def _retry_after_seconds(error):

    match = re.search(
        r"retry in ([\d.]+)s|retryDelay\W+([\d.]+)s",
        _error_text(error)
    )

    if match:
        return float(match.group(1) or match.group(2)) + 1

    try:
        return float(error.response.headers.get("retry-after")) + 1
    except (AttributeError, TypeError, ValueError):
        return 60


def _is_invalid_key_error(error):

    if isinstance(error, (AuthenticationError, PermissionDeniedError)):
        return True

    # Gemini responde 400 "API key not valid" / "API_KEY_INVALID".
    return (
        isinstance(error, BadRequestError)
        and "api key" in str(error).lower().replace("_", " ")
    )


# =========================================================
# COMPLETION
# =========================================================
#
# Las claves se prueban en círculo empezando por la activa:
#
#   - cupo diario agotado (429 PerDay): la clave se marca como
#     agotada hasta medianoche del Pacífico y se pasa a la
#     siguiente; así se suman los cupos de todos los proyectos.
#   - límite por minuto (429): la clave se pausa lo que indique
#     Gemini y se pasa a la siguiente.
#   - clave inválida: se pausa esa clave y se pasa a la siguiente.
#   - otro error (caída, timeout, modelo, ubicación no admitida):
#     afecta a todas las claves; se pausa el proveedor.
# =========================================================

def complete(
    system_prompt,
    user_text,
    max_tokens
):

    if not PROVIDERS:

        raise RuntimeError(
            "IA desactivada: configura ia_proveedores.json "
            "o GEMINI_API_KEY."
        )

    errors = []

    for round_number in (1, 2):

        soonest_retry = None

        for provider in PROVIDERS:

            name = provider["nombre"]

            cooldown = _cooldown_until.get(name, 0)

            if cooldown > time.time():

                soonest_retry = min(soonest_retry or cooldown, cooldown)

                continue

            n_keys = len(provider["clients"])

            first_key = provider["clave_activa"]

            response = None

            for offset in range(n_keys):

                key_idx = (first_key + offset) % n_keys

                key_id = _key_id(provider, key_idx)

                label = f"{name} clave #{key_idx + 1}"

                cooldown = _cooldown_until.get(key_id, 0)

                if cooldown > time.time():

                    soonest_retry = min(soonest_retry or cooldown, cooldown)

                    continue

                if not _reserve_request(provider, key_idx):

                    errors.append(f"{label}: cupo diario agotado")

                    continue

                if key_idx != provider["clave_activa"]:

                    print(f"[AI] {name}: se usa la clave #{key_idx + 1}")

                    provider["clave_activa"] = key_idx

                try:

                    response = provider["clients"][key_idx].chat.completions.create(
                        model=provider["modelo"],
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_text}
                        ],
                        max_tokens=max_tokens
                    )

                    break

                except RateLimitError as error:

                    if _is_daily_quota_error(error):

                        _mark_exhausted(provider, key_idx)

                        print(
                            f"[AI] {label}: cupo diario agotado "
                            f"(límite real del proyecto: {_quota_value(error)}); "
                            f"se pasa a la siguiente clave"
                        )

                        errors.append(f"{label}: cupo diario agotado")

                        continue

                    wait = _retry_after_seconds(error)

                    _cooldown_until[key_id] = time.time() + wait

                    soonest_retry = min(
                        soonest_retry or _cooldown_until[key_id],
                        _cooldown_until[key_id]
                    )

                    print(f"[AI] {label}: límite por minuto; pausa {wait:.0f}s")

                    errors.append(f"{label}: límite por minuto")

                    continue

                except APIStatusError as error:

                    if _is_invalid_key_error(error):

                        _cooldown_until[key_id] = (
                            time.time() + ERROR_COOLDOWN_SECONDS
                        )

                        print(f"[AI] {label}: clave no válida; se pasa a la siguiente")

                        errors.append(f"{label}: clave no válida")

                        continue

                    _cooldown_until[name] = time.time() + ERROR_COOLDOWN_SECONDS

                    print(f"[AI] {name}: error {error!r:.200}")

                    errors.append(f"{name}: {type(error).__name__}")

                    break

                except (APITimeoutError, APIConnectionError) as error:

                    _cooldown_until[name] = time.time() + ERROR_COOLDOWN_SECONDS

                    print(f"[AI] {name}: error {error!r:.200}")

                    errors.append(f"{name}: {type(error).__name__}")

                    break

            if response is None:
                continue

            if response.usage:

                print(
                    f"[AI TEXT] {name}/{provider['modelo']} "
                    f"clave #{provider['clave_activa'] + 1} tokens:",
                    f"entrada={response.usage.prompt_tokens}",
                    f"salida={response.usage.completion_tokens}"
                )

            choice = response.choices[0]

            # Un texto cortado a mitad de frase no debe llegar al Word.
            if choice.finish_reason == "length":

                errors.append(f"{name}: superó {max_tokens} tokens")

                continue

            return (choice.message.content or "").strip(), name

        # Todas las claves en límite por minuto: se espera una vez
        # si es corto.
        if (
            round_number == 1
            and soonest_retry
            and soonest_retry - time.time() <= RATE_LIMIT_MAX_WAIT
        ):

            wait = max(0, soonest_retry - time.time())

            print(f"[AI] Todas las claves en límite; espera {wait:.0f}s")

            time.sleep(wait)

            continue

        break

    raise RuntimeError(
        "Ningún proveedor de IA disponible: "
        + "; ".join(dict.fromkeys(errors))
    )
