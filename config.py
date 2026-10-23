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

def get_env_var(name: str) -> str:
    """Obtiene una variable de entorno obligatoria o lanza una excepción clara."""
    value = os.environ.get(name, "").strip()
    if not value:
        raise ValueError(
            f"Falta la variable de entorno obligatoria '{name}'. "
            f"Asegúrate de configurarla en los Secrets de tu repositorio en GitHub."
        )
    return value

def get_email_credentials():
    """Lee y valida las credenciales de correo desde os.environ."""
    gmail_user = get_env_var("GMAIL_USER")
    gmail_app_password = get_env_var("GMAIL_APP_PASSWORD").replace(" ", "")
    recipient = os.environ.get("ALERT_RECIPIENT_EMAIL", "").strip() or gmail_user
    return gmail_user, gmail_app_password, recipient
