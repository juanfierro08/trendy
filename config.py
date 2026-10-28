import os
from pathlib import Path

# Directorio raíz y archivo de estado
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
ESTADO_FILE = DATA_DIR / "estado.json"

# Tienda VTEX
VTEX_BASE_URL = "https://www.maquillajetrendyshop.com"
VTEX_SEARCH_ENDPOINT = f"{VTEX_BASE_URL}/api/catalog_system/pub/products/search"

# Términos vigilados (ampliados para máxima cobertura y detección temprana)
MONITORED_TERMS = [
    "adviento",
    "calendario de adviento",
    "calendario adviento",
    "calendario",
    "coalendario",
    "preventa",
    "pre venta",
    "preventa adviento",
    "caja adviento",
    "navidad",
    "calendario trendy",
    "edicion especial adviento"
]

# User-Agent estándar
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
    "Referer": "https://www.maquillajetrendyshop.com/",
    "Origin": "https://www.maquillajetrendyshop.com"
}

import re

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$")

def mask_email(email: str) -> str:
    """Enmascara una dirección de correo para los logs (ej: 'ju***@gmail.com')."""
    if not email or not isinstance(email, str):
        return "***"
    cleaned = email.strip()
    if "@" not in cleaned:
        return f"{cleaned[:2]}***" if len(cleaned) >= 2 else "***"
    user_part, domain_part = cleaned.split("@", 1)
    if len(user_part) <= 1:
        masked_user = f"{user_part}***" if user_part else "***"
    else:
        masked_user = f"{user_part[:2]}***"
    return f"{masked_user}@{domain_part}"

def validate_email(email: str, var_name: str = "ALERT_RECIPIENT_EMAIL") -> str:
    """Valida que el correo no esté vacío, no contenga 'gmmail' y tenga formato válido."""
    if not email or not isinstance(email, str):
        raise ValueError(
            f"Falta la variable de entorno obligatoria '{var_name}' o está vacía. "
            f"Asegúrate de configurarla en los Secrets de tu repositorio en GitHub."
        )
    cleaned = email.strip()
    if not cleaned:
        raise ValueError(
            f"La variable de entorno obligatoria '{var_name}' no puede estar vacía. "
            f"Asegúrate de configurarla en los Secrets de tu repositorio en GitHub."
        )
    if "gmmail" in cleaned.lower():
        raise ValueError(
            f"El correo '{mask_email(cleaned)}' configurado en '{var_name}' contiene 'gmmail' en lugar de 'gmail'. "
            f"Por favor corrige la variable de entorno {var_name}."
        )
    if not EMAIL_REGEX.match(cleaned):
        raise ValueError(
            f"El correo '{mask_email(cleaned)}' configurado en '{var_name}' no tiene un formato válido (ejemplo esperado: usuario@gmail.com)."
        )
    return cleaned

def get_env_var(name: str) -> str:
    """Obtiene una variable de entorno obligatoria o lanza una excepción clara."""
    value = os.environ.get(name, "").strip()
    if not value:
        raise ValueError(
            f"Falta la variable de entorno obligatoria '{name}'. "
            f"Asegúrate de configurarla en los Secrets de tu repositorio en GitHub."
        )
    return value

def get_recipient_email() -> str:
    """Obtiene y valida el destinatario exclusivamente desde os.environ['ALERT_RECIPIENT_EMAIL']."""
    if "ALERT_RECIPIENT_EMAIL" not in os.environ:
        raise ValueError(
            "Falta la variable de entorno obligatoria 'ALERT_RECIPIENT_EMAIL'. "
            "Asegúrate de configurarla en los Secrets de tu repositorio en GitHub sin valores por defecto."
        )
    return validate_email(os.environ["ALERT_RECIPIENT_EMAIL"], "ALERT_RECIPIENT_EMAIL")

def get_email_credentials():
    """Lee y valida las credenciales de correo desde os.environ."""
    gmail_user = validate_email(get_env_var("GMAIL_USER"), "GMAIL_USER")
    gmail_app_password = get_env_var("GMAIL_APP_PASSWORD").replace(" ", "")
    recipient = get_recipient_email()
    return gmail_user, gmail_app_password, recipient
