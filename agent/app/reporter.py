import requests
import socket
import platform
from datetime import datetime

SERVER_URL = "http://localhost:8000/api/agent/report"

def send(results):
    payload = {
        "agent": {
            "id": socket.gethostname(),
            "hostname": socket.gethostname(),
            "ip": socket.gethostbyname(socket.gethostname()),
            "os": platform.system().lower(),
            "os_version": platform.version()
        },
        "policy": {
            "name": "base-ubuntu",
            "version": "1.0"
        },
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "results": results
    }

    r = requests.post(SERVER_URL, json=payload)
    print("SERVER RESPONSE:", r.status_code, r.text)