import requests
import datetime
import time
import random
import threading

URL = "http://127.0.0.1:5000/logs"

# Tokens de los servicios
TOKENS = {
    "servicio-a": "TOKEN_SERVICIO_A",
    "servicio-b": "TOKEN_SERVICIO_B",
    "servicio-c": "TOKEN_SERVICIO_C_FAKE"  # ejemplo de token inválido
}

# Niveles de log
NIVELES = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# -----------------------
# Funciones auxiliares
# -----------------------
def ahora_iso():
    """Devuelve timestamp ISO UTC."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def generar_log(servicio):
    """Genera un log aleatorio para un servicio."""
    return {
        "timestamp": ahora_iso(),
        "service": servicio,
        "severity": random.choice(NIVELES),
        "message": f"Mensaje de prueba desde {servicio} - {random.randint(1,9999)}",
        "meta": {"pid": random.randint(1000,9999)}
    }

def enviar_batch(servicio, batch_size=5):
    """Envía un batch de logs al servidor."""
    token = TOKENS.get(servicio)
    headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}
    logs = [generar_log(servicio) for _ in range(batch_size)]

    try:
        r = requests.post(URL, json=logs, headers=headers, timeout=5)
        print(f"[{servicio}] Batch {batch_size} logs -> status={r.status_code}")
    except Exception as e:
        print(f"[{servicio}] Error al enviar batch: {e}")

def enviar_log_individual(servicio):
    """Envía un log individual al servidor."""
    token = TOKENS.get(servicio)
    log = generar_log(servicio)
    headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}

    try:
        r = requests.post(URL, json=log, headers=headers, timeout=3)
        print(f"[{servicio}] {log['severity']} -> status={r.status_code}")
    except Exception as e:
        print(f"[{servicio}] Error al enviar log individual: {e}")

# -----------------------
# Worker de servicio
# -----------------------
def servicio_worker(servicio, interval=1.0, batch=False):
    """Simula un servicio enviando logs cada interval + aleatorio."""
    while True:
        if batch:
            enviar_batch(servicio, batch_size=random.randint(3, 8))
        else:
            enviar_log_individual(servicio)
        time.sleep(interval + random.random() * 1.5)

# -----------------------
# Main
# -----------------------
if __name__ == "__main__":
    # Servicios a simular
    servicios = ["servicio-a", "servicio-b", "servicio-c"]
    threads = []

    # Arrancamos un hilo por servicio
    for s in servicios:
        t = threading.Thread(target=servicio_worker, args=(s, 1.0, False), daemon=True)
        threads.append(t)
        t.start()

    print("Simulación de servicios iniciada. Ctrl+C para detener.")

    # Mantener vivo
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Simulación detenida.")
