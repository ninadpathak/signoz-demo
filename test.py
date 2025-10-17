import sys
import time

import requests
from requests import RequestException

BASE_URL = "http://localhost:5001"
WORKLOAD = [
    ("POST", "/createOrder", "order run"),
    ("GET", "/checkInventory", "inventory ping"),
]


def wait_for_ready(timeout_seconds=15):
    """Ping the health endpoint until the service becomes available."""
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=1)
            if response.status_code == 200:
                return True
        except RequestException:
            time.sleep(0.5)
    return False


print("Generating test traffic...")

if not wait_for_ready():
    print(
        "Order Service is not reachable at http://localhost:5001. "
        "Start it first with `python3 app.py` (inside the virtualenv)."
    )
    sys.exit(1)

for batch in range(20):
    for method, path, label in WORKLOAD:
        try:
            reply = requests.request(method, f"{BASE_URL}{path}", timeout=3)
            print(f"{label} {batch+1}: {reply.status_code}")
        except RequestException as err:
            print(f"{label} {batch+1} failed: {err}")
    time.sleep(1)

print("Done! Check SigNoz cloud")
