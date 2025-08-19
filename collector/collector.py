!/usr/bin/env python3
import time
import json
import requests
import os

# ---------------- CONFIGURATION ----------------
LOGSTASH_URL = "http://<IP_ELK>:5000"  # change with the IP of the ELK VM
LOG_FILES = {
    "keystone": "/var/snap/microstack/common/log/keystone.log",
    "nova": "/var/snap/microstack/common/log/nova.log",
    "neutron": "/var/snap/microstack/common/log/neutron.log"
}
POLL_INTERVAL = 1  # seconds between checks

# Saves the last position read for each file so collector
# does not always reread the entire log, but only the new lines.
file_positions = {}

# ---------------- FUNCTIONS ----------------
# Function fot to build a JSON event
# sending event to Logstash
# if there is an answere different by 200 (OK) signal an error
# and if there is a connection error print "Errore invio" (Error in sending)
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

# Function that read new row to avoid to lost logs.
# If we don't have an offset yet, let's start from the end of the file.
def tail_log(service, filepath):
    if service not in file_positions:
        file_positions[service] = os.path.getsize(filepath)

    with open(filepath, "r") as f:
        f.seek(file_positions[service])        # Go to last read position
        lines = f.readlines()                  # Go to new row
        for line in lines:
            send_to_logstash(service, line)    # Send every row to Logstash
        file_positions[service] = f.tell()     # Upload current location

# ---------------- MAIN CICLE ----------------
# The infinite while cicle:
# 1. scrolls services and their logs LOG_FILES (Keystone, Neutron, Nova)
# 2. if the file exists reads and send a new line
# 3. it waits POOL_INTERVALS (1 second setted before) and starts again
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

