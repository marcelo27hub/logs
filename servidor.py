#importmaos librerias que usaremos

from flask import flask, request, jsonify
from datetime import datetime, timezone
import sqlite3

app = flask(__name__)

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
    "TOKEN_SERVICIO_B" : "servicio-b"
} 
#funcion para la hora y fecha actual 
def fecha_hora_actual():
    return datetime.now(timezone.utc).isoformat()

#funcion para verificar si el el token del log esta autorizado
def verificar_token():
    autorizacion = request.headers.get("Autorisacion", "")
    if not autorizacion.startswith("Token "):
        return None
    token = autorizacion.split(" ")[1].strip()
    if token in tokens_validos:
        return token 
    return None

#la ruta logs para irnos a la base de datos y hacer peticiones al servidor con post
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
        fecha_evento = log.get("timestamp", fecha_hora_actual())
        servicio = log.get("service", tokens_validos[token])
        nivel = log.get("severity", "INFO")
        mensaje = log.get("message", "")
        recibido_en = fecha_hora_actual()
        
        cursor.excute("""
            INSERT INTO logs (fecha_evento, servicio, nivel, mensaje, recibido_en)
            VALUES (?, ?, ?, ?, ?)
            """), (fecha_evento, servicio, nivel, mensaje, recibido_en)
        conexion.commit()
        conexion.close()
        return jsonify({"ok": True, "guardados": len(lista_de_logs)}), 201     
    
