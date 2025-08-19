!/usr/bin/env python3
import time
import json
import requests
import os

# ---------------- CONFIGURAZIONE ----------------
LOGSTASH_URL = "http://<IP_ELK>:5000"  # cambia con l'IP della VM ELK
LOG_FILES = {
    "keystone": "/var/snap/microstack/common/log/keystone.log",
    "nova": "/var/snap/microstack/common/log/nova.log",
    "neutron": "/var/snap/microstack/common/log/neutron.log"
}
POLL_INTERVAL = 1  # secondi tra un controllo e l'altro

# Memorizza l'ultima posizione letta per ogni file
file_positions = {}

# ---------------- FUNZIONI ----------------
def send_to_logstash(service, line):
    event = {
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime()),
        "service": service,
        "message": line.strip()
    }
    try:
        response = requests.post(LOGSTASH_URL, json=event, timeout=1)
        if response.status_code != 200:
            print(f"[!] Errore invio {service}: {response.status_code}")
    except Exception as e:
        print(f"[!] Eccezione invio {service}: {e}")
        
def tail_log(service, filepath):
    # Se non abbiamo ancora un offset, iniziamo dalla fine del file
    if service not in file_positions:
        file_positions[service] = os.path.getsize(filepath)

    with open(filepath, "r") as f:
        f.seek(file_positions[service])
        lines = f.readlines()
        for line in lines:
            send_to_logstash(service, line)
        file_positions[service] = f.tell()

# ---------------- CICLO PRINCIPALE ----------------
if __name__ == "__main__":
    print("[*] Avvio collector OpenStack")
    try:
        while True:
            for service, logfile in LOG_FILES.items():
                if os.path.exists(logfile):
                    tail_log(service, logfile)
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("\n[*] Collector terminato")
