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

    