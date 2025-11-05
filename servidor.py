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
def hora_actual():
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