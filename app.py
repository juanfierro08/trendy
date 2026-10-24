import os
import sys
from pathlib import Path
from flask import Flask, send_from_directory, jsonify, request

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import config
import monitor
import notifier

app = Flask(__name__, static_folder="docs", static_url_path="")

@app.route("/")
def index():
    return send_from_directory("docs", "index.html")

@app.route("/data/<path:path>")
def get_data(path):
    return send_from_directory("data", path)

@app.route("/api/test-email", methods=["POST"])
def api_test_email():
    try:
        monitor.run_test_email()
        return jsonify({"success": True, "message": "Correo de prueba enviado con éxito."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/simulate", methods=["POST"])
def api_simulate():
    try:
        monitor.run_simulate()
        return jsonify({"success": True, "message": "Detección simulada y correo de alerta enviado."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/reset", methods=["POST"])
def api_reset():
    try:
        monitor.run_reset()
        return jsonify({"success": True, "message": "Radar reiniciado a no disponible."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/check-now", methods=["POST"])
def api_check_now():
    try:
        monitor.run_single_check()
        return jsonify({"success": True, "message": "Revisión completada."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    print(f"\n=======================================================")
    print(f"  ✨ TRENDY RADAR - SERVIDOR LOCAL ✨")
    print(f"=======================================================")
    print(f"  * Panel web: http://127.0.0.1:5000")
    print(f"  * Tienda: {config.VTEX_BASE_URL}")
    print(f"=======================================================\n")
    app.run(host="127.0.0.1", port=5000, debug=False)
