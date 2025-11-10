#importamos librerias que usaremos

from flask import Flask, request, jsonify
from datetime import datetime, timezone
import sqlite3

app = Flask(__name__)

base_de_datos = "logs.db"

#para inicializar nuestra base de datos
def inicializar_db():
    conexion = sqlite3.connect(base_de_datos) 
    cursor = conexion.cursor()
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
    conexion.close()

inicializar_db()

tokens_validos = {
    "TOKEN_SERVICIO_A" : "servicio-a",
    "TOKEN_SERVICIO_B" : "servicio-b",
    "TOKEN_SERVICIO_C" : "servicio-c",
    
} 
#funcion para la hora y fecha actual 
def fecha_hora_actual():
    return datetime.now(timezone.utc).isoformat()

#funcion para verificar si el el token del log esta autorizado
def verificar_token():
    autorizacion = request.headers.get("Authorization", "")
    if not isinstance(autorizacion, str):
        return None
    if not autorizacion.startswith("Token "):
        return None
    token = autorizacion.split(" ")[1].strip()
    if token in tokens_validos:
        return token 
    return None

#quiero que mi servidor reciba logs cuando el cliente haga post
@app.route("/logs", methods = ["POST"])

#para recibir logs
def recibir_logs():
    token = verificar_token()
    if not token:
        return jsonify({"error": "Quien sos, bro?"}), 401
    
    datos = request.get_json(silent=True)
    if not datos:
        return jsonify({"error": "JSON inválido"}), 400
    
    #permitir lista de logs o un solo log
    lista_de_logs = datos if isinstance(datos, list) else [datos]
    
    conexion = sqlite3.connect(base_de_datos)
    cursor = conexion.cursor()
    for log in lista_de_logs:
        fecha_hora_evento = log.get("timestamp", fecha_hora_actual())
        servicio = log.get("service", tokens_validos[token])
        nivel = log.get("severity", "INFO")
        mensaje = log.get("message", "")
        recibido_en = fecha_hora_actual()
        
        cursor.execute("""
            INSERT INTO logs (fecha_hora_evento, servicio, nivel, mensaje, recibido_en)
            VALUES (?, ?, ?, ?, ?)
            """, (fecha_hora_evento, servicio, nivel, mensaje, recibido_en))
    conexion.commit()
    conexion.close()
    return jsonify({"ok": True, "guardados": len(lista_de_logs)}), 201     
    
#endpoint para consultar logs
@app.route("/logs", methods = ["GET"])
def consultar_logs():

    #recibir filtros opcionales desde la URL
    fecha_inicio_evento = request.args.get("timestamp_start")        # fecha_hora_evento >=
    fecha_fin_evento = request.args.get("timestamp_end")            # fecha_hora_evento <=
    fecha_inicio_recibido = request.args.get("received_at_start")     # recibido_en >=
    fecha_fin_recibido = request.args.get("received_at_end")         # recibido_en <=

    # Base de la consulta_sql dinámica
    consulta_sql = "SELECT * FROM logs WHERE 1=1"
    valores_parametros = []

    #aplicar filtros si existen
    if fecha_inicio_evento:
        consulta_sql += " AND fecha_hora_evento >= ?"
        valores_parametros.append(fecha_inicio_evento)

    if fecha_fin_evento:
        consulta_sql += " AND fecha_hora_evento <= ?"
        valores_parametros.append(fecha_fin_evento)

    if fecha_inicio_recibido:
        consulta_sql += " AND recibido_en >= ?"
        valores_parametros.append(fecha_inicio_recibido)

    if fecha_fin_recibido:
        consulta_sql += " AND recibido_en <= ?"
        valores_parametros.append(fecha_fin_recibido)

    consulta_sql += " ORDER BY id DESC"

    # Ejecutar consulta
    conexion = sqlite3.connect(base_de_datos)
    cursor = conexion.cursor()
    cursor.execute(consulta_sql, valores_parametros)
    filas = cursor.fetchall()
    conexion.close()

    # Convertir a JSON
    logs = []
    for fila in filas:
        logs.append({
            "id": fila[0],
            "fecha_hora_evento": fila[1],
            "servicio": fila[2],
            "nivel": fila[3],
            "mensaje": fila[4],
            "recibido_en": fila[5],
        })

    return jsonify({"cantidad": len(logs), "logs": logs})



#ejecutar el servidor
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)