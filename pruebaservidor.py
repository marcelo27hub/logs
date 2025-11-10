# servidor.py (versión extendida en español: filtros, stats, limpieza)
from flask import Flask, request, jsonify
from datetime import datetime, timezone
import sqlite3

app = Flask(__name__)
base_de_datos = "logs.db"

# -----------------------
# Inicialización de la Base de Datos (con WAL para concurrencia)
# -----------------------
def inicializar_base():
    with sqlite3.connect(base_de_datos) as conexion:
        cursor = conexion.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora_evento TEXT,
                servicio TEXT,
                nivel TEXT,
                mensaje TEXT,
                recibido_en TEXT
            )
        """)
        conexion.commit()

inicializar_base()

# -----------------------
# Tokens válidos (hardcoded)
# -----------------------
tokens_validos = {
    "TOKEN_SERVICIO_A": "servicio-a",
    "TOKEN_SERVICIO_B": "servicio-b"
}

# -----------------------
# Utilidades
# -----------------------
def ahora_iso():
    return datetime.now(timezone.utc).isoformat()

def verificar_token():
    autorizacion = request.headers.get("Authorization", "")
    if not isinstance(autorizacion, str) or not autorizacion.startswith("Token "):
        return None

    token = autorizacion.split(" ", 1)[1].strip()
    return token if token in tokens_validos else None

# Validar ISO en filtros
def iso_seguro(valor):
    if not valor:
        return None
    try:
        datetime.fromisoformat(valor)
        return valor
    except Exception:
        return None

# -----------------------
# POST /logs : recibir logs
# -----------------------
@app.route("/logs", methods=["POST"])
def recibir_logs():
    token = verificar_token()
    if not token:
        return jsonify({"error": "Quién sos, bro?"}), 401

    datos = request.get_json(silent=True)
    if not datos:
        return jsonify({"error": "JSON inválido"}), 400

    lista_logs = datos if isinstance(datos, list) else [datos]

    with sqlite3.connect(base_de_datos) as conexion:
        cursor = conexion.cursor()
        for log in lista_logs:
            fecha_evento = log.get("timestamp", ahora_iso())
            servicio = log.get("service", tokens_validos[token])
            nivel = log.get("severity", "INFO")
            mensaje = log.get("message", "")
            recibido_en = ahora_iso()

            cursor.execute("""
                INSERT INTO logs (fecha_hora_evento, servicio, nivel, mensaje, recibido_en)
                VALUES (?, ?, ?, ?, ?)
            """, (fecha_evento, servicio, nivel, mensaje, recibido_en))

    return jsonify({"ok": True, "guardados": len(lista_logs)}), 201

# -----------------------
# GET /logs : consultar logs con filtros
# -----------------------
@app.route("/logs", methods=["GET"])
def consultar_logs():
    fecha_evento_inicio = iso_seguro(request.args.get("timestamp_start"))
    fecha_evento_fin = iso_seguro(request.args.get("timestamp_end"))
    recibido_inicio = iso_seguro(request.args.get("received_at_start"))
    recibido_fin = iso_seguro(request.args.get("received_at_end"))
    servicio = request.args.get("servicio")
    nivel = request.args.get("nivel")

    consulta = "SELECT * FROM logs WHERE 1=1"
    parametros = []

    if servicio:
        consulta += " AND servicio = ?"
        parametros.append(servicio)
    if nivel:
        consulta += " AND nivel = ?"
        parametros.append(nivel)
    if fecha_evento_inicio:
        consulta += " AND fecha_hora_evento >= ?"
        parametros.append(fecha_evento_inicio)
    if fecha_evento_fin:
        consulta += " AND fecha_hora_evento <= ?"
        parametros.append(fecha_evento_fin)
    if recibido_inicio:
        consulta += " AND recibido_en >= ?"
        parametros.append(recibido_inicio)
    if recibido_fin:
        consulta += " AND recibido_en <= ?"
        parametros.append(recibido_fin)

    consulta += " ORDER BY id DESC"

    with sqlite3.connect(base_de_datos) as conexion:
        cursor = conexion.cursor()
        cursor.execute(consulta, parametros)
        filas = cursor.fetchall()

    logs = [
        {
            "id": f[0],
            "fecha_hora_evento": f[1],
            "servicio": f[2],
            "nivel": f[3],
            "mensaje": f[4],
            "recibido_en": f[5]
        }
        for f in filas
    ]

    return jsonify({"cantidad": len(logs), "logs": logs})

# -----------------------
# GET /stats : estadísticas
# -----------------------
@app.route("/stats", methods=["GET"])
def estadisticas():
    with sqlite3.connect(base_de_datos) as conexion:
        cursor = conexion.cursor()

        # Cantidad por servicio
        cursor.execute("SELECT servicio, COUNT(*) FROM logs GROUP BY servicio")
        por_servicio = dict(cursor.fetchall())

        # Cantidad por nivel
        cursor.execute("SELECT nivel, COUNT(*) FROM logs GROUP BY nivel")
        por_nivel = dict(cursor.fetchall())

        # Último log de cada servicio
        cursor.execute("""
            SELECT l.servicio, l.id, l.fecha_hora_evento, l.nivel, l.mensaje, l.recibido_en
            FROM logs l
            JOIN (
                SELECT servicio, MAX(id) AS maxid FROM logs GROUP BY servicio
            ) ult ON l.servicio = ult.servicio AND l.id = ult.maxid
        """)

        ultimos_logs = [
            {
                "servicio": r[0],
                "id": r[1],
                "fecha_hora_evento": r[2],
                "nivel": r[3],
                "mensaje": r[4],
                "recibido_en": r[5]
            }
            for r in cursor.fetchall()
        ]

    return jsonify({
        "logs_por_servicio": por_servicio,
        "logs_por_nivel": por_nivel,
        "ultimo_log_por_servicio": ultimos_logs
    })

# -----------------------
# DELETE /logs : limpieza de logs viejos
# -----------------------
@app.route("/logs", methods=["DELETE"])
def limpiar_logs():
    antes_de = iso_seguro(request.args.get("before"))
    if not antes_de:
        return jsonify({"error": "El parámetro 'before' debe ser una fecha ISO válida"}), 400

    with sqlite3.connect(base_de_datos) as conexion:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM logs WHERE fecha_hora_evento < ?", (antes_de,))
        eliminados = cursor.rowcount
        conexion.commit()

    return jsonify({"ok": True, "eliminados": eliminados})

# -----------------------
# Ejecutar servidor
# -----------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
