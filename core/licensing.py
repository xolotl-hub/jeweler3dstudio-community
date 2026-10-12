"""
Jeweler 3D Studio - Gumroad License API & Activation Engine
Handles license verification with Gumroad API and offline caching.
"""

import hashlib
import json
import os
import platform
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, Optional, Tuple

GUMROAD_VERIFY_URL = "https://api.gumroad.com/v1/licenses/verify"

# Permalinks de productos en Gumroad según el tier
PRODUCT_PERMALINKS = {
    "community": None,
    "essential": "jeweler3d-essential",
    "standard":  "jeweler3d-standard",
    "pro":       "jeweler3d-pro",
    "xolotllab": None,
}


def _get_cache_dir() -> Path:
    """Returns directory for storing encrypted license tokens."""
    home = Path.home()
    if platform.system() == "Windows":
        cache_dir = Path(os.environ.get("APPDATA", home)) / "Jeweler3DStudio"
    else:
        cache_dir = home / ".config" / "jeweler3dstudio"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _get_machine_fingerprint() -> str:
    """Returns local system fingerprint for offline activation token locking."""
    raw = f"{platform.node()}-{platform.machine()}-{platform.processor()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def verify_gumroad_license(
    license_key: str,
    product_permalink: str = "jeweler3d-essential",
    increment_uses_count: bool = True,
) -> Tuple[bool, str, Dict]:
    """
    Verifies license key against official Gumroad API.
    Returns (success, message, purchase_info_dict).
    """
    cleaned_key = license_key.strip()
    if not cleaned_key:
        return False, "La clave de licencia no puede estar vacía.", {}

    payload = {
        "product_permalink": product_permalink,
        "license_key": cleaned_key,
        "increment_uses_count": "true" if increment_uses_count else "false",
    }

    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(
        GUMROAD_VERIFY_URL,
        data=data,
        headers={
            "User-Agent": "Jeweler3DStudio-Blender/1.0",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            res_code = response.getcode()
            body = response.read().decode("utf-8")
            res_json = json.loads(body)

            if res_code == 200 and res_json.get("success"):
                purchase = res_json.get("purchase", {})
                if purchase.get("subscription_cancelled_at"):
                    return False, "La suscripción de Gumroad ha sido cancelada.", purchase
                if purchase.get("subscription_failed_at"):
                    return False, "El cobro de la suscripción falló. Actualiza tu método de pago.", purchase

                # Guardar token de activación offline
                save_offline_token(cleaned_key, product_permalink, purchase)
                return True, "Licencia verificada y activada con éxito.", purchase
            else:
                msg = res_json.get("message", "Clave de licencia no válida en Gumroad.")
                return False, msg, res_json

    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8")
            err_json = json.loads(err_body)
            msg = err_json.get("message", f"Error {e.code}: Licencia inválida.")
            return False, msg, {}
        except Exception:
            return False, f"Error {e.code} al contactar Gumroad: Clave inválida.", {}
    except urllib.error.URLError as e:
        # Fallback offline si no hay conexión
        if is_offline_token_valid(cleaned_key, product_permalink):
            return True, "Licencia activa (modo offline validado).", {}
        return False, f"No se pudo conectar a Gumroad ({e.reason}). Conéctate a internet para activar.", {}
    except Exception as e:
        return False, f"Error inesperado al validar: {e}", {}


def save_offline_token(license_key: str, product_permalink: str, purchase_info: dict) -> None:
    """Saves local signed token for offline validation."""
    cache_file = _get_cache_dir() / f"license_{product_permalink}.json"
    fingerprint = _get_machine_fingerprint()
    token_data = {
        "key_hash": hashlib.sha256(license_key.encode("utf-8")).hexdigest(),
        "permalink": product_permalink,
        "email": purchase_info.get("email", ""),
        "variants": purchase_info.get("variants", ""),
        "fingerprint": fingerprint,
    }
    try:
        cache_file.write_text(json.dumps(token_data, indent=2), encoding="utf-8")
    except Exception:
        pass


def is_offline_token_valid(license_key: str, product_permalink: str) -> bool:
    """Validates locally cached token without internet connection."""
    cache_file = _get_cache_dir() / f"license_{product_permalink}.json"
    if not cache_file.exists():
        return False
    try:
        data = json.loads(cache_file.read_text(encoding="utf-8"))
        k_hash = hashlib.sha256(license_key.strip().encode("utf-8")).hexdigest()
        fp = _get_machine_fingerprint()
        return (data.get("key_hash") == k_hash and
                data.get("permalink") == product_permalink and
                data.get("fingerprint") == fp)
    except Exception:
        return False


def clear_offline_token(product_permalink: str) -> None:
    """Removes cached activation token."""
    cache_file = _get_cache_dir() / f"license_{product_permalink}.json"
    if cache_file.exists():
        try:
            cache_file.unlink()
        except Exception:
            pass
