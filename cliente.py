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
    
def enviar_multiples_logs(lista_mensajes):
    logs = []

    for texto in lista_mensajes:
        logs.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "servicio-a",
            "severity": "INFO",
            "message": texto
        })

    respuesta = requests.post(servidor_url, headers=HEADERS, data=json.dumps(logs))

    print("STATUS:", respuesta.status_code)
    print("RESPUESTA:", respuesta.json())
    
    def consultar_logs():
        respuesta = requests.get(servidor_url)
        print("STATUS:", respuesta.status_code)
        datos = respuesta.json()

        print(f"Cantidad de logs: {datos['cantidad']}")
        for log in datos["logs"]:
            print(log)