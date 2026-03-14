import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import json
from typing import Optional

import paho.mqtt.client as mqtt

from app.config import (
    BROKER_HOST,
    BROKER_PORT,
    MQTT_KEEPALIVE,
    TOPIC_TEMPERATURE,
    TOPIC_BUTTON,
    TOPIC_AC_SET,
    TOPIC_SYSTEM_STATUS,
    TOPIC_SYSTEM_ALERT,
    TEMP_WARNING_THRESHOLD,
    TEMP_ALARM_THRESHOLD,
    CLIENT_ID_MANAGER,
)
from app.database import (
    init_db,
    insert_sensor_data,
    insert_actuator_event,
    insert_system_log,
)
from app.utils import now_str


latest_temperature: Optional[float] = None
ac_state: str = "OFF"


def evaluate_temperature_status(value: float) -> str:
    if value >= TEMP_ALARM_THRESHOLD:
        return "ALARM"
    if value >= TEMP_WARNING_THRESHOLD:
        return "WARNING"
    return "NORMAL"


def log_event(level: str, message: str) -> None:
    insert_system_log(level, message, now_str())


def publish_system_status(client: mqtt.Client, status: str, message: str) -> None:
    payload = {
        "timestamp": now_str(),
        "status": status,
        "message": message,
    }
    client.publish(TOPIC_SYSTEM_STATUS, json.dumps(payload))
    log_event(status, message)


def publish_system_alert(client: mqtt.Client, level: str, message: str) -> None:
    payload = {
        "timestamp": now_str(),
        "level": level,
        "message": message,
    }
    client.publish(TOPIC_SYSTEM_ALERT, json.dumps(payload))
    log_event(level, message)


def set_ac_state(client: mqtt.Client, new_state: str, reason: str) -> None:
    global ac_state

    new_state = new_state.upper().strip()

    if new_state not in {"ON", "OFF"}:
        return

    if ac_state == new_state:
        return

    ac_state = new_state
    timestamp = now_str()

    payload = {
        "timestamp": timestamp,
        "device": "ac_relay",
        "command": ac_state,
        "reason": reason,
    }

    client.publish(TOPIC_AC_SET, json.dumps(payload))
    insert_actuator_event("ac_relay", ac_state, timestamp)
    log_event("INFO", f"AC changed to {ac_state} ({reason})")

    publish_system_status(client, "INFO", f"AC turned {ac_state} ({reason})")


def handle_temperature_message(client: mqtt.Client, payload: dict) -> None:
    global latest_temperature

    try:
        value = float(payload["value"])
    except (KeyError, TypeError, ValueError):
        publish_system_alert(client, "ERROR", "Invalid temperature payload received")
        return

    timestamp = payload.get("timestamp", now_str())
    unit = payload.get("unit", "C")

    latest_temperature = value
    status = evaluate_temperature_status(value)

    insert_sensor_data(
        device="temperature_sensor",
        value=value,
        unit=unit,
        timestamp=timestamp,
        status=status,
    )

    publish_system_status(
        client,
        status,
        f"Temperature received: {value}{unit}",
    )

    if status == "ALARM":
        publish_system_alert(
            client,
            "ALARM",
            f"High temperature detected: {value}{unit}",
        )
        set_ac_state(client, "ON", "automatic alarm handling")
    elif status == "WARNING":
        publish_system_alert(
            client,
            "WARNING",
            f"Temperature warning: {value}{unit}",
        )
        set_ac_state(client, "ON", "automatic warning handling")
    else:
        set_ac_state(client, "OFF", "temperature back to normal")


def handle_button_message(client: mqtt.Client, payload: dict) -> None:
    command = str(payload.get("command", "")).upper().strip()

    if command == "AC_ON":
        log_event("INFO", "Manual button command received: AC_ON")
        set_ac_state(client, "ON", "manual button command")
    elif command == "AC_OFF":
        log_event("INFO", "Manual button command received: AC_OFF")
        set_ac_state(client, "OFF", "manual button command")
    else:
        publish_system_alert(client, "ERROR", f"Unknown button command: {command}")


def on_connect(client: mqtt.Client, userdata, flags, rc):
    if rc == 0:
        print(f"[Manager] Connected to broker at {BROKER_HOST}:{BROKER_PORT}")
        client.subscribe(TOPIC_TEMPERATURE)
        client.subscribe(TOPIC_BUTTON)
        print(f"[Manager] Subscribed to: {TOPIC_TEMPERATURE}")
        print(f"[Manager] Subscribed to: {TOPIC_BUTTON}")
        publish_system_status(client, "INFO", "Manager connected and ready")
    else:
        print(f"[Manager] Connection failed with code {rc}")
        log_event("ERROR", f"Manager connection failed with code {rc}")


def on_message(client: mqtt.Client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except json.JSONDecodeError:
        publish_system_alert(client, "ERROR", f"Invalid JSON on topic {msg.topic}")
        return

    print(f"[Manager] Message received on {msg.topic}: {payload}")

    if msg.topic == TOPIC_TEMPERATURE:
        handle_temperature_message(client, payload)
    elif msg.topic == TOPIC_BUTTON:
        handle_button_message(client, payload)


def main() -> None:
    init_db()

    client = mqtt.Client(client_id=CLIENT_ID_MANAGER, clean_session=True)
    client.on_connect = on_connect
    client.on_message = on_message

    print("[Manager] Starting manager...")
    log_event("INFO", "Manager process started")
    client.connect(BROKER_HOST, BROKER_PORT, MQTT_KEEPALIVE)
    client.loop_forever()


if __name__ == "__main__":
    main()