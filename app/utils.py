from datetime import datetime
import json


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def build_message(device: str, value, unit: str = "", extra: dict | None = None) -> str:
    payload = {
        "device": device,
        "value": value,
        "unit": unit,
        "timestamp": now_str(),
    }

    if extra:
        payload.update(extra)

    return json.dumps(payload)


def parse_message(payload: bytes) -> dict:
    return json.loads(payload.decode("utf-8"))