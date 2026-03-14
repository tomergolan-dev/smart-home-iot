from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "smarthome.db"

BROKER_HOST = "broker.hivemq.com"
BROKER_PORT = 1883
MQTT_KEEPALIVE = 60

TOPIC_TEMPERATURE = "smarthome/room1/temperature"
TOPIC_BUTTON = "smarthome/room1/button"
TOPIC_AC_SET = "smarthome/room1/ac/set"
TOPIC_AC_STATUS = "smarthome/room1/ac/status"
TOPIC_SYSTEM_STATUS = "smarthome/room1/system/status"
TOPIC_SYSTEM_ALERT = "smarthome/room1/system/alert"

TEMP_WARNING_THRESHOLD = 30.0
TEMP_ALARM_THRESHOLD = 35.0

CLIENT_ID_MANAGER = "smart-home-manager"
CLIENT_ID_GUI = "smart-home-gui"
CLIENT_ID_TEMP_SENSOR = "smart-home-temp-sensor"
CLIENT_ID_BUTTON = "smart-home-button"
CLIENT_ID_AC_RELAY = "smart-home-ac-relay"