# Smart Home IoT Monitoring System

A Python-based Smart Home monitoring system developed as part of an **IoT course project**.

The system simulates a smart home environment where sensors, actuators and a control manager communicate using **MQTT**.  
It monitors temperature, triggers alerts and automatically controls an air conditioner.

---

# System Architecture

The system is composed of several independent components communicating through MQTT topics.

Temperature Sensor → Manager → AC Relay  
Button Emulator → Manager  
Manager → GUI  
Manager → SQLite Database

### Components

- **Temperature Sensor Emulator** – simulates temperature readings
- **Button Emulator** – simulates a manual ON/OFF button
- **AC Relay Emulator** – simulates an air-conditioner relay
- **Manager** – receives sensor data, applies rules and controls the AC
- **GUI** – displays system status and temperature trends
- **SQLite Database** – stores logs and system history

---

# Technologies

- Python 3.14
- MQTT (`paho-mqtt`)
- SQLite
- Tkinter GUI
- Matplotlib (temperature graph)

---

# Features

- Real-time temperature monitoring
- Automatic AC activation when temperature exceeds threshold
- Manual AC control through GUI or button emulator
- Event logging system
- Temperature graph visualization
- History viewer (sensor, actuator and system logs)
- SQLite database storage

---

## Installation

Install dependencies:

#### Windows
```bash
python -m pip install -r requirements.txt
```

#### macOS
```bash
python3 -m pip install -r requirements.txt
```

---

## Option 1 - Run everything automatically

#### Windows
```bash
./run_all.bat
```

#### macOS
Run once to give execute permission:
```bash
chmod +x run_all.sh
```
Run the system:
```bash
./run_all.sh
```

This starts all system components in separate terminals.

---

## Option 2 – Run components manually

Open separate terminals and run:

### Windows

#### Temperature Sensor

```bash
python emulators/temperature_sensor.py
```

#### Button Emulator

```bash
python emulators/button_emulator.py
```

#### AC Relay

```bash
python emulators/ac_relay.py
```

#### System Manager

```bash
python manager/manager.py
```

#### GUI

```bash
python gui/gui.py
```
### macOS

> ⚠️ Note: On macOS and Linux, use `python3` instead of `python` when running commands.
---

# MQTT Topics

| Topic | Description |
|------|-------------|
| `smarthome/room1/temperature` | Temperature sensor data |
| `smarthome/room1/button` | Manual button commands |
| `smarthome/room1/ac/set` | AC control commands |
| `smarthome/room1/ac/status` | AC state updates |
| `smarthome/room1/system/status` | System information |
| `smarthome/room1/system/alert` | System alerts |

---

# Database

The system stores history in:

```
data/smarthome.db
```

Tables:

- `sensor_data` – temperature readings
- `actuator_events` – AC ON/OFF events
- `system_logs` – system messages

---

# GUI

The graphical interface displays:

- Current temperature
- System status
- AC state
- Temperature graph
- Event log
- System history viewer

---

# Project Structure

```
smart-home-iot
│
├── sensors
│   └── temperature_sensor.py
│
├── emulators
│   └── button_emulator.py
│
├── actuators
│   └── ac_relay.py
│
├── manager
│   └── manager.py
│
├── gui
│   └── gui.py
│
├── app
│   ├── config.py
│   ├── database.py
│   └── utils.py
│
├── data
│   └── smarthome.db
│
├── run_all.bat
├── requirements.txt
└── README.md
```

---

# Notes

This project simulates a real IoT environment using software components only.  
All devices communicate through a public MQTT broker.

---

# Author

Smart Home IoT Project – Course Assignment
