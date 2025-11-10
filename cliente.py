#librerias que usare en mi cliente para enviar los logs
import requests
import json
from datetime import datetime, timezone
import time

servidor_url = "http://127.0.0.1:5000/logs"
# Tokens de varios servicios
SERVICIOS = {
    "TOKEN_SERVICIO_A": "servicio-a",
    "TOKEN_SERVICIO_B": "servicio-b"
}


# Niveles de severidad posibles
NIVELES = ["INFO", "DEBUG", "ERROR"]

def enviar_log(token, mensaje, nivel= "INFO", servicio = "servicio-a"):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {token}"
    }
    log= {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": servicio,
        "severity": nivel,
        "message": mensaje

    }
    respuesta = requests.post(servidor_url, headers=headers, data=json.dumps(log))
    print(f"[{servicio} - {nivel}] STATUS: {respuesta.status_code} | RESPUESTA: {respuesta.json()}")

    
def enviar_multiples_logs_fijos(cantidad_por_nivel=3):
    niveles_servicios = {
        "INFO": ("TOKEN_SERVICIO_A", "servicio-a", "Todo funcionando correctamente"),
        "DEBUG": ("TOKEN_SERVICIO_C", "servicio-c", "Debugging proceso interno"),
        "ERROR": ("TOKEN_SERVICIO_B", "servicio-b", "Se detectó un error crítico")
    }

    for nivel, (token, servicio, mensaje_base) in niveles_servicios.items():
        for i in range(cantidad_por_nivel):
            mensaje = f"{mensaje_base} #{i+1}"
            enviar_log(token, mensaje, nivel, servicio)
            time.sleep(0.2)

    
def consultar_logs():
    respuesta = requests.get(servidor_url)
    print("STATUS:", respuesta.status_code)
    datos = respuesta.json()

    print(f"Cantidad de logs: {datos['cantidad']}")
    for log in datos["logs"]:
        print(log)
            
if __name__ == "__main__":
    print("Enviando logs simples y múltiples con niveles y servicios distintos...")
    enviar_multiples_logs_fijos(3)

    print("\nConsultando todos los logs...")
    consultar_logs()