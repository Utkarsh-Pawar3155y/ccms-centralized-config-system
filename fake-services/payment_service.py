import requests
import time
import websocket
import json
import threading

CCMS_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"

SERVICE_NAME = "payment-service"
ENVIRONMENT = "prod"

# 🔥 GLOBAL CONFIG STORE (VERY IMPORTANT)
configs = {}


# -----------------------------
# FETCH CONFIGS (INITIAL LOAD)
# -----------------------------
def fetch_configs():
    url = f"{CCMS_URL}/configs/{SERVICE_NAME}/{ENVIRONMENT}"

    print(f"Fetching configs from CCMS: {url}")

    response = requests.get(url)

    if response.status_code != 200:
        print("Failed to fetch configs:", response.text)
        return {}

    data = response.json()

    result = {}

    for config in data["configs"]:
        result[config["key"]] = config["value"]

    return result


# -----------------------------
# APPLY CONFIG UPDATE (REAL MAGIC)
# -----------------------------
def apply_update(update):
    global configs

    key = update["key"]
    value = update["value"]

    old_value = configs.get(key)

    configs[key] = value

    print("\n🔥 CONFIG UPDATED IN SERVICE:")
    print(f"{key}: {old_value} → {value}")


# -----------------------------
# WEBSOCKET HANDLERS
# -----------------------------
def on_message(ws, message):
    data = json.loads(message)

    if data.get("service") == SERVICE_NAME:
        apply_update(data)


def on_open(ws):
    print("Connected to CCMS WebSocket...")


def on_error(ws, error):
    print("WebSocket error:", error)


def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")


# -----------------------------
# START WEBSOCKET LISTENER
# -----------------------------
def start_websocket():
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    ws.run_forever()


# -----------------------------
# MAIN SERVICE
# -----------------------------
def start_service():
    global configs

    print("\n🚀 Starting payment-service (REAL-TIME)...\n")

    # Initial load
    configs = fetch_configs()

    print("\n📦 Initial Configurations:")
    for key, value in configs.items():
        print(f"{key} = {value}")

    # Start WebSocket in background
    threading.Thread(target=start_websocket, daemon=True).start()

    # Simulate service running
    while True:
        time.sleep(5)
        print("\n💡 Service using configs:")
        for key, value in configs.items():
            print(f"{key} = {value}")


if __name__ == "__main__":
    start_service()