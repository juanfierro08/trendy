import json
import time
import sys
from datetime import datetime, timezone
from typing import Dict, Any, List
import requests

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import config
import notifier

def load_estado() -> Dict[str, Any]:
    """Carga el estado guardado desde data/estado.json."""
    default_state = {
        "avisado": False,
        "ultima_revision": None,
        "estado": "no disponible",
        "historial": []
    }
    if config.ESTADO_FILE.exists():
        try:
            with open(config.ESTADO_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    # Asegurar campos requeridos
                    data.setdefault("avisado", False)
                    data.setdefault("ultima_revision", None)
                    data.setdefault("estado", "no disponible")
                    if not isinstance(data.get("historial"), list):
                        data["historial"] = []
                    return data
        except Exception as e:
            print(f"[Aviso] No se pudo leer {config.ESTADO_FILE}: {e}. Se creará nuevo estado.")
    return default_state

def save_estado(estado: Dict[str, Any]):
    """Guarda el estado actualizado en data/estado.json manteniendo máximo 50 entradas de historial."""
    try:
        if "historial" in estado and isinstance(estado["historial"], list):
            estado["historial"] = estado["historial"][:50]
            
        with open(config.ESTADO_FILE, "w", encoding="utf-8") as f:
            json.dump(estado, f, ensure_ascii=False, indent=2)
        print(f"[Estado] Archivo {config.ESTADO_FILE} actualizado correctamente.")
    except Exception as e:
        print(f"[Error] No se pudo guardar {config.ESTADO_FILE}: {e}")

def parse_product(item: Dict[str, Any], term: str, now_iso: str) -> Dict[str, Any]:
    """Extrae los campos relevantes de un producto de VTEX."""
    prod_id = str(item.get("productId") or "")
    prod_name = item.get("productName", "Sin nombre")
    link = item.get("link", config.VTEX_BASE_URL)
    
    price = None
    available = False
    try:
        offer = item["items"][0]["sellers"][0]["commertialOffer"]
        price = offer.get("Price")
        available = offer.get("AvailableQuantity", 0) > 0
    except Exception:
        pass

    return {
        "productId": prod_id,
        "productName": prod_name,
        "price": price,
        "link": link,
        "available": available,
        "term": term,
        "detected_at": now_iso
    }

def run_single_check():
    """Ejecuta una única revisión contra la tienda VTEX y termina."""
    now_iso = datetime.now(timezone.utc).isoformat()
    now_display = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    print("=" * 60)
    print(f"🎯 TRENDY RADAR • REVISIÓN [{now_display}]")
    print(f"Tienda objetivo: {config.VTEX_BASE_URL}")
    print("=" * 60)

    estado = load_estado()
    detected_products: List[Dict[str, Any]] = []
    seen_ids = set()
    has_network_error = False
    error_detail = ""

    for term in config.MONITORED_TERMS:
        start_t = time.time()
        encoded_term = requests.utils.quote(term)
        target_url = f"{config.VTEX_SEARCH_ENDPOINT}?ft={encoded_term}&_from=0&_to=49"
        print(f"\n[Consulta] Buscando término: '{term}'...")

        try:
            resp = requests.get(
                target_url,
                headers=config.REQUEST_HEADERS,
                timeout=15
            )
            elapsed_ms = (time.time() - start_t) * 1000

            if resp.status_code in (200, 206):
                data = resp.json()
                count = len(data) if isinstance(data, list) else 0
                print(f"[Respuesta] Código HTTP {resp.status_code} ({elapsed_ms:.1f}ms) - {count} producto(s) encontrado(s)")

                if count > 0:
                    for item in data:
                        parsed = parse_product(item, term, now_iso)
                        pid = parsed["productId"]
                        if pid and pid not in seen_ids:
                            seen_ids.add(pid)
                            detected_products.append(parsed)
                            print(f"   👉 ID={pid} | {parsed['productName']} | Precio: {parsed['price']} | {parsed['link']}")
            else:
                has_network_error = True
                error_detail = f"VTEX respondió con código HTTP {resp.status_code}"
                print(f"[Aviso] {error_detail} ({elapsed_ms:.1f}ms)")

        except requests.exceptions.RequestException as req_err:
            has_network_error = True
            error_detail = f"Fallo de conexión: {str(req_err)}"
            print(f"[Error] Error en consulta para '{term}': {req_err}")

    # Determinar estado y registrar en historial
    estado["ultima_revision"] = now_iso
    historial = estado.get("historial", [])
    if not isinstance(historial, list):
        historial = []

    if has_network_error and not detected_products:
        # Error de red sin productos
        estado["estado"] = "error"
        resultado_msg = f"Error al consultar VTEX: {error_detail}"
        print(f"\n[Resultado] {resultado_msg}")
        historial.insert(0, {
            "fecha": now_iso,
            "resultado": resultado_msg
        })
    elif detected_products:
        # Productos detectados (disponible)
        estado["estado"] = "disponible"
        cant = len(detected_products)
        resultado_msg = f"¡Calendario disponible! Se encontraron {cant} producto(s) en Trendy Shop."
        print("\n" + "!" * 60)
        print(f"🚨 {resultado_msg}")
        print("!" * 60)

        # Enviar correo solo si no se ha avisado previamente
        if not estado.get("avisado", False):
            print("\n[Correo] 'avisado' es False. Despachando alerta por Gmail SMTP...")
            notifier.send_alert(detected_products)
            estado["avisado"] = True
            resultado_msg += " (Alerta por correo enviada)."
            print("[Correo] ¡Alerta enviada exitosamente!")
        else:
            print("\n[Correo] 'avisado' ya es True. Se omite envío de correo para evitar duplicados.")
            resultado_msg += " (Ya se había notificado previamente)."

        historial.insert(0, {
            "fecha": now_iso,
            "resultado": resultado_msg
        })
    else:
        # 0 productos (no disponible)
        estado["estado"] = "no disponible"
        resultado_msg = "Revisión completada: 0 productos encontrados. El calendario aún no sale a la venta."
        print(f"\n[Resultado] {resultado_msg}")
        historial.insert(0, {
            "fecha": now_iso,
            "resultado": resultado_msg
        })

    # Guardar estado actualizado con máx 50 registros de historial
    save_estado(estado)
    print("\n[Fin] Ejecución finalizada correctamente.")

if __name__ == "__main__":
    run_single_check()
