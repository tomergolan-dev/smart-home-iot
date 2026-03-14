import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import json

import paho.mqtt.client as mqtt

from app.config import (
    BROKER_HOST,
    BROKER_PORT,
    MQTT_KEEPALIVE,
    TOPIC_AC_SET,
    TOPIC_AC_STATUS,
    CLIENT_ID_AC_RELAY,
)
from app.utils import now_str


ac_state = "OFF"


def publish_status(client: mqtt.Client, state: str, reason: str) -> None:
    payload = {
        "device": "ac_relay",
        "state": state,
        "reason": reason,
        "timestamp": now_str(),
    }
    client.publish(TOPIC_AC_STATUS, json.dumps(payload))
    print(f"[AC Relay] Published status to {TOPIC_AC_STATUS}: {payload}")


def on_connect(client: mqtt.Client, userdata, flags, rc):
    if rc == 0:
        print(f"[AC Relay] Connected to broker at {BROKER_HOST}:{BROKER_PORT}")
        client.subscribe(TOPIC_AC_SET)
        print(f"[AC Relay] Subscribed to: {TOPIC_AC_SET}")
    else:
        print(f"[AC Relay] Connection failed with code {rc}")


def on_message(client: mqtt.Client, userdata, msg):
    global ac_state

    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except json.JSONDecodeError:
        print("[AC Relay] Invalid JSON received")
        return

    print(f"[AC Relay] Message received on {msg.topic}: {payload}")

    command = str(payload.get("command", "")).upper().strip()
    reason = str(payload.get("reason", "no reason provided"))

    if command not in {"ON", "OFF"}:
        print(f"[AC Relay] Invalid command: {command}")
        return

    ac_state = command
    print(f"[AC Relay] AC state changed to: {ac_state}")

    publish_status(client, ac_state, reason)


def main() -> None:
    client = mqtt.Client(client_id=CLIENT_ID_AC_RELAY, clean_session=True)
    client.on_connect = on_connect
    client.on_message = on_message

    print("[AC Relay] Starting AC relay emulator...")
    client.connect(BROKER_HOST, BROKER_PORT, MQTT_KEEPALIVE)
    client.loop_forever()


if __name__ == "__main__":
    main()