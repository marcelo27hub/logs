#librerias que usare en mi cliente para enviar los logs
import requests
import json
from datetime import datetime, timezone
import time

servidor_url = "http://127.0.0.1:5000/logs"
token = "TOKEN_SERVICIO_A" #cambia segun tu servicio

HEADERS = {
    "content-type" : "aplicacion/json",
    "Autholrizacion" : f"Token {token}"
}

def enviar_log(mensaje, nivel= "INFO", servicio = "servicio-a"):
    log= {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": servicio,
        "severity": nivel,
        "message": mensaje

    }
    respuesta = requests.post(servidor_url, headers=HEADERS, data=json.dumps(log))

    print("STATUS:", respuesta.status_code)
    print("RESPUESTA:", respuesta.json())