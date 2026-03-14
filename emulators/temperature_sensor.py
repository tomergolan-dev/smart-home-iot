import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import json
import random
import time

import paho.mqtt.client as mqtt

from app.config import (
    BROKER_HOST,
    BROKER_PORT,
    MQTT_KEEPALIVE,
    TOPIC_TEMPERATURE,
    CLIENT_ID_TEMP_SENSOR,
)
from app.utils import now_str


MIN_TEMP = 20.0
MAX_TEMP = 40.0
PUBLISH_INTERVAL_SECONDS = 5


def generate_temperature() -> float:
    return round(random.uniform(MIN_TEMP, MAX_TEMP), 1)


def build_payload(value: float) -> str:
    payload = {
        "device": "temperature_sensor",
        "value": value,
        "unit": "C",
        "timestamp": now_str(),
    }
    return json.dumps(payload)


def on_connect(client: mqtt.Client, userdata, flags, rc):
    if rc == 0:
        print(f"[Temperature Sensor] Connected to broker at {BROKER_HOST}:{BROKER_PORT}")
    else:
        print(f"[Temperature Sensor] Connection failed with code {rc}")


def main() -> None:
    client = mqtt.Client(client_id=CLIENT_ID_TEMP_SENSOR, clean_session=True)
    client.on_connect = on_connect

    print("[Temperature Sensor] Starting temperature sensor emulator...")
    client.connect(BROKER_HOST, BROKER_PORT, MQTT_KEEPALIVE)
    client.loop_start()

    try:
        while True:
            temperature = generate_temperature()
            payload = build_payload(temperature)

            client.publish(TOPIC_TEMPERATURE, payload)
            print(f"[Temperature Sensor] Published to {TOPIC_TEMPERATURE}: {payload}")

            time.sleep(PUBLISH_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\n[Temperature Sensor] Stopped by user.")

    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()