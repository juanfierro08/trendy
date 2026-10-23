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
    if config.ESTADO_FILE.exists():
        try:
            with open(config.ESTADO_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception as e:
            print(f"[Aviso] No se pudo leer {config.ESTADO_FILE}: {e}. Se creará nuevo estado.")
    return {
        "avisado": False,
        "ultima_revision": None,
        "productos_detectados": []
    }

def save_estado(estado: Dict[str, Any]):
    """Guarda el estado actualizado en data/estado.json."""
    try:
        with open(config.ESTADO_FILE, "w", encoding="utf-8") as f:
            json.dump(estado, f, ensure_ascii=False, indent=2)
        print(f"[Estado] Archivo {config.ESTADO_FILE} actualizado correctamente.")
    except Exception as e:
        print(f"[Error] No se pudo guardar {config.ESTADO_FILE}: {e}")

def parse_product(item: Dict[str, Any], term: str) -> Dict[str, Any]:
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
        "detected_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    }

def run_single_check():
    """Ejecuta una única revisión contra la API de VTEX y termina."""
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print("=" * 60)
    print(f"🎯 TRENDY RADAR • EJECUCIÓN ÚNICA [{now_str}]")
    print(f"Tienda: {config.VTEX_BASE_URL}")
    print("=" * 60)

    estado = load_estado()

    # Si ya se envió la alerta en una ejecución anterior, no repetir el correo
    if estado.get("avisado", False):
        print("[Monitor] ⚠️ El aviso ya fue enviado previamente según data/estado.json.")
        print(f"          Fecha del aviso anterior: {estado.get('fecha_aviso', 'Desconocida')}")
        print("          Para evitar spam no se enviará otro correo. Finalizando ejecución.")
        estado["ultima_revision"] = now_str
        save_estado(estado)
        return

    detected_products: List[Dict[str, Any]] = []
    seen_ids = set()

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
                        parsed = parse_product(item, term)
                        pid = parsed["productId"]
                        if pid and pid not in seen_ids:
                            seen_ids.add(pid)
                            detected_products.append(parsed)
                            print(f"   👉 ID={pid} | {parsed['productName']} | Precio: {parsed['price']} | {parsed['link']}")
            else:
                print(f"[Aviso] VTEX respondió con código HTTP {resp.status_code} ({elapsed_ms:.1f}ms)")

        except requests.exceptions.RequestException as req_err:
            print(f"[Error] Falló la petición a VTEX para '{term}': {req_err}")

    # Evaluar resultados
    estado["ultima_revision"] = now_str

    if detected_products:
        print("\n" + "!" * 60)
        print(f"🚨 ¡¡SE DETECTARON {len(detected_products)} PRODUCTO(S) DE ADVIENTO!!")
        print("!" * 60)

        # Enviar correo de alerta (si falla lanzará excepción)
        notifier.send_alert(detected_products)

        # Marcar como avisado para no volver a enviar correos repetidos
        estado["avisado"] = True
        estado["fecha_aviso"] = now_str
        estado["productos_detectados"] = detected_products
        save_estado(estado)
        print("\n[Éxito] Alerta enviada y estado guardado con avisado=True.")
    else:
        print(f"\n[Resultado] No se encontró el Calendario de Adviento en esta revisión.")
        save_estado(estado)
        print("[Fin] Revisión completada con éxito.")

if __name__ == "__main__":
    run_single_check()
