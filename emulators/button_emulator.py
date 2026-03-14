import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import json

import paho.mqtt.client as mqtt

from app.config import (
    BROKER_HOST,
    BROKER_PORT,
    MQTT_KEEPALIVE,
    TOPIC_BUTTON,
    CLIENT_ID_BUTTON,
)
from app.utils import now_str


def build_payload(command: str) -> str:
    payload = {
        "device": "button_emulator",
        "command": command,
        "timestamp": now_str(),
    }
    return json.dumps(payload)


def on_connect(client: mqtt.Client, userdata, flags, rc):
    if rc == 0:
        print(f"[Button Emulator] Connected to broker at {BROKER_HOST}:{BROKER_PORT}")
    else:
        print(f"[Button Emulator] Connection failed with code {rc}")


def main() -> None:
    client = mqtt.Client(client_id=CLIENT_ID_BUTTON, clean_session=True)
    client.on_connect = on_connect

    print("[Button Emulator] Starting button emulator...")
    client.connect(BROKER_HOST, BROKER_PORT, MQTT_KEEPALIVE)
    client.loop_start()

    print("[Button Emulator] Type one of the following commands:")
    print("  on   -> send AC_ON")
    print("  off  -> send AC_OFF")
    print("  exit -> close the emulator")

    try:
        while True:
            user_input = input("Enter command (on/off/exit): ").strip().lower()

            if user_input == "exit":
                print("[Button Emulator] Exiting...")
                break

            if user_input == "on":
                command = "AC_ON"
            elif user_input == "off":
                command = "AC_OFF"
            else:
                print("[Button Emulator] Invalid command. Please type on, off, or exit.")
                continue

            payload = build_payload(command)
            client.publish(TOPIC_BUTTON, payload)
            print(f"[Button Emulator] Published to {TOPIC_BUTTON}: {payload}")

    except KeyboardInterrupt:
        print("\n[Button Emulator] Stopped by user.")

    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()