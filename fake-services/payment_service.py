import requests
import time

CCMS_URL = "http://localhost:8000"
SERVICE_NAME = "payment-service"
ENVIRONMENT = "prod"


def fetch_configs():
    url = f"{CCMS_URL}/configs/{SERVICE_NAME}/{ENVIRONMENT}"

    print(f"Fetching configs from CCMS: {url}")

    response = requests.get(url)

    if response.status_code != 200:
        print("Failed to fetch configs:", response.text)
        return {}

    data = response.json()

    configs = {}

    for config in data["configs"]:
        configs[config["key"]] = config["value"]

    return configs


def start_service():
    print("\nStarting payment-service...\n")

    configs = fetch_configs()

    print("\nLoaded Configurations:")

    for key, value in configs.items():
        print(f"{key} = {value}")

    print("\nService running...\n")


if __name__ == "__main__":
    start_service()