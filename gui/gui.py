import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import json
import queue
import tkinter as tk
from tkinter import ttk

import paho.mqtt.client as mqtt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from app.config import (
    BROKER_HOST,
    BROKER_PORT,
    MQTT_KEEPALIVE,
    TOPIC_SYSTEM_STATUS,
    TOPIC_SYSTEM_ALERT,
    TOPIC_AC_STATUS,
    TOPIC_BUTTON,
    CLIENT_ID_GUI,
)
from app.database import (
    init_db,
    get_recent_sensor_history,
    get_recent_actuator_history,
    get_recent_system_logs,
)


message_queue: queue.Queue = queue.Queue()


class SmartHomeGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Smart Home IoT System")
        self.root.geometry("1100x850")
        self.root.state("zoomed")

        self.temperature_var = tk.StringVar(value="N/A")
        self.system_status_var = tk.StringVar(value="N/A")
        self.ac_state_var = tk.StringVar(value="OFF")
        self.last_message_var = tk.StringVar(value="System started")

        self.client: mqtt.Client | None = None
        self.toggle_button = None

        self._build_layout()
        self.root.after(500, self.process_queue)
        self.root.after(2000, self.refresh_temperature_graph)

    def _build_layout(self) -> None:
        outer_frame = ttk.Frame(self.root)
        outer_frame.pack(fill="both", expand=True)

        self.main_canvas = tk.Canvas(outer_frame, highlightthickness=0)
        self.main_canvas.pack(side="left", fill="both", expand=True)

        main_scrollbar = ttk.Scrollbar(
            outer_frame,
            orient="vertical",
            command=self.main_canvas.yview,
        )
        main_scrollbar.pack(side="right", fill="y")

        self.main_canvas.configure(yscrollcommand=main_scrollbar.set)

        self.container = ttk.Frame(self.main_canvas, padding=20)
        self.canvas_window = self.main_canvas.create_window(
            (0, 0),
            window=self.container,
            anchor="nw",
        )

        self.container.bind("<Configure>", self._on_frame_configure)
        self.main_canvas.bind("<Configure>", self._on_canvas_configure)

        self.root.bind_all("<MouseWheel>", self._on_mousewheel)

        title = ttk.Label(
            self.container,
            text="Smart Home Monitoring System",
            font=("Arial", 20, "bold"),
        )
        title.pack(pady=(0, 20))

        cards_frame = ttk.Frame(self.container)
        cards_frame.pack(fill="x", pady=(0, 15))

        self._create_info_card(cards_frame, "Temperature", self.temperature_var, 0, 0)
        self._create_info_card(cards_frame, "System Status", self.system_status_var, 0, 1)
        self._create_info_card(cards_frame, "AC State", self.ac_state_var, 0, 2)

        button_frame = ttk.Frame(self.container)
        button_frame.pack(fill="x", pady=(0, 15))

        self.toggle_button = ttk.Button(
            button_frame,
            text="Turn AC ON",
            command=self.toggle_ac,
        )
        self.toggle_button.pack(side="left")

        history_button = ttk.Button(
            button_frame,
            text="View History",
            command=self.open_history_window,
        )
        history_button.pack(side="right")

        chart_frame = ttk.LabelFrame(self.container, text="Temperature Trend", padding=10)
        chart_frame.pack(fill="x", pady=(0, 15))

        self.figure = Figure(figsize=(9.0, 2.1), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Recent Temperature Readings")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("°C")

        self.canvas = FigureCanvasTkAgg(self.figure, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill="x", expand=True)

        last_message_frame = ttk.LabelFrame(self.container, text="Last Message", padding=15)
        last_message_frame.pack(fill="x", pady=(0, 15))

        last_message_label = ttk.Label(
            last_message_frame,
            textvariable=self.last_message_var,
            font=("Arial", 11),
            wraplength=980,
            justify="left",
        )
        last_message_label.pack(anchor="w")

        log_frame = ttk.LabelFrame(self.container, text="Event Log", padding=10)
        log_frame.pack(fill="both", expand=True, pady=(0, 10))

        log_inner_frame = ttk.Frame(log_frame)
        log_inner_frame.pack(fill="both", expand=True)

        log_scrollbar = ttk.Scrollbar(log_inner_frame, orient="vertical")
        log_scrollbar.pack(side="right", fill="y")

        self.log_text = tk.Text(
            log_inner_frame,
            height=12,
            state="disabled",
            yscrollcommand=log_scrollbar.set,
            wrap="word",
        )
        self.log_text.pack(side="left", fill="both", expand=True)

        log_scrollbar.config(command=self.log_text.yview)

    def _on_frame_configure(self, event=None) -> None:
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))

    def _on_canvas_configure(self, event) -> None:
        self.main_canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event) -> None:
        self.main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _create_info_card(
        self,
        parent: ttk.Frame,
        title: str,
        variable: tk.StringVar,
        row: int,
        column: int,
    ) -> None:
        frame = ttk.LabelFrame(parent, text=title, padding=15)
        frame.grid(row=row, column=column, padx=8, pady=8, sticky="nsew")

        value_label = ttk.Label(
            frame,
            textvariable=variable,
            font=("Arial", 16, "bold"),
            width=18,
            anchor="center",
        )
        value_label.pack()

        parent.grid_columnconfigure(column, weight=1)

    def append_log(self, text: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def update_toggle_button(self) -> None:
        state = self.ac_state_var.get().strip().upper()
        if state == "ON":
            self.toggle_button.config(text="Turn AC OFF")
        else:
            self.toggle_button.config(text="Turn AC ON")

    def toggle_ac(self) -> None:
        if self.client is None:
            self.append_log("[GUI] MQTT client not ready")
            return

        current_state = self.ac_state_var.get().strip().upper()
        command = "AC_OFF" if current_state == "ON" else "AC_ON"

        payload = {
            "device": "button_emulator",
            "command": command,
        }

        self.client.publish(TOPIC_BUTTON, json.dumps(payload))
        self.append_log(f"[GUI] Manual command sent: {command}")

    def refresh_temperature_graph(self) -> None:
        rows = get_recent_sensor_history("temperature_sensor", limit=12)
        rows = list(reversed(rows))

        values = []
        labels = []

        for row in rows:
            timestamp, value, unit, status = row
            values.append(float(value))
            labels.append(timestamp.split(" ")[1] if " " in timestamp else timestamp)

        self.ax.clear()
        self.ax.set_title("Recent Temperature Readings")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("°C")

        if values:
            self.ax.plot(labels, values, marker="o")
            self.ax.tick_params(axis="x", rotation=30)
        else:
            self.ax.text(0.5, 0.5, "No data yet", ha="center", va="center")
            self.ax.set_xticks([])
            self.ax.set_yticks([])

        self.figure.tight_layout()
        self.canvas.draw()

        self.root.after(3000, self.refresh_temperature_graph)

    def open_history_window(self) -> None:
        history_window = tk.Toplevel(self.root)
        history_window.title("System History")
        history_window.geometry("900x650")
        history_window.resizable(False, False)

        notebook = ttk.Notebook(history_window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        sensor_frame = ttk.Frame(notebook, padding=10)
        actuator_frame = ttk.Frame(notebook, padding=10)
        logs_frame = ttk.Frame(notebook, padding=10)

        notebook.add(sensor_frame, text="Temperature History")
        notebook.add(actuator_frame, text="AC History")
        notebook.add(logs_frame, text="System Logs")

        self._build_sensor_history(sensor_frame)
        self._build_actuator_history(actuator_frame)
        self._build_logs_history(logs_frame)

    def _build_sensor_history(self, parent: ttk.Frame) -> None:
        columns = ("timestamp", "value", "unit", "status")
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=22)

        tree.heading("timestamp", text="Timestamp")
        tree.heading("value", text="Value")
        tree.heading("unit", text="Unit")
        tree.heading("status", text="Status")

        tree.column("timestamp", width=220)
        tree.column("value", width=120)
        tree.column("unit", width=80)
        tree.column("status", width=120)

        rows = get_recent_sensor_history("temperature_sensor", limit=50)
        for row in rows:
            tree.insert("", "end", values=row)

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _build_actuator_history(self, parent: ttk.Frame) -> None:
        columns = ("timestamp", "action")
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=22)

        tree.heading("timestamp", text="Timestamp")
        tree.heading("action", text="Action")

        tree.column("timestamp", width=250)
        tree.column("action", width=150)

        rows = get_recent_actuator_history("ac_relay", limit=50)
        for row in rows:
            tree.insert("", "end", values=row)

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _build_logs_history(self, parent: ttk.Frame) -> None:
        columns = ("timestamp", "level", "message")
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=22)

        tree.heading("timestamp", text="Timestamp")
        tree.heading("level", text="Level")
        tree.heading("message", text="Message")

        tree.column("timestamp", width=220)
        tree.column("level", width=100)
        tree.column("message", width=500)

        rows = get_recent_system_logs(limit=100)
        for row in rows:
            tree.insert("", "end", values=row)

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def process_queue(self) -> None:
        while not message_queue.empty():
            item = message_queue.get()

            item_type = item.get("type")
            payload = item.get("payload", {})

            if item_type == "system_status":
                status = str(payload.get("status", "N/A"))
                message = str(payload.get("message", ""))
                timestamp = str(payload.get("timestamp", ""))

                self.system_status_var.set(status)
                self.last_message_var.set(message)
                self.append_log(f"[{timestamp}] STATUS - {status}: {message}")

                if "Temperature received:" in message:
                    temp_text = message.replace("Temperature received:", "").strip()
                    self.temperature_var.set(temp_text)

            elif item_type == "system_alert":
                level = str(payload.get("level", "N/A"))
                message = str(payload.get("message", ""))
                timestamp = str(payload.get("timestamp", ""))

                self.system_status_var.set(level)
                self.last_message_var.set(message)
                self.append_log(f"[{timestamp}] ALERT - {level}: {message}")

            elif item_type == "ac_status":
                state = str(payload.get("state", "N/A"))
                reason = str(payload.get("reason", ""))
                timestamp = str(payload.get("timestamp", ""))

                self.ac_state_var.set(state)
                self.last_message_var.set(f"AC is now {state} ({reason})")
                self.append_log(f"[{timestamp}] AC - {state}: {reason}")
                self.update_toggle_button()

        self.root.after(500, self.process_queue)


def on_connect(client: mqtt.Client, userdata, flags, rc):
    if rc == 0:
        print(f"[GUI] Connected to broker at {BROKER_HOST}:{BROKER_PORT}")
        client.subscribe(TOPIC_SYSTEM_STATUS)
        client.subscribe(TOPIC_SYSTEM_ALERT)
        client.subscribe(TOPIC_AC_STATUS)

        print(f"[GUI] Subscribed to: {TOPIC_SYSTEM_STATUS}")
        print(f"[GUI] Subscribed to: {TOPIC_SYSTEM_ALERT}")
        print(f"[GUI] Subscribed to: {TOPIC_AC_STATUS}")
    else:
        print(f"[GUI] Connection failed with code {rc}")


def on_message(client: mqtt.Client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except json.JSONDecodeError:
        print(f"[GUI] Invalid JSON received on topic {msg.topic}")
        return

    print(f"[GUI] Message received on {msg.topic}: {payload}")

    if msg.topic == TOPIC_SYSTEM_STATUS:
        message_queue.put({"type": "system_status", "payload": payload})
    elif msg.topic == TOPIC_SYSTEM_ALERT:
        message_queue.put({"type": "system_alert", "payload": payload})
    elif msg.topic == TOPIC_AC_STATUS:
        message_queue.put({"type": "ac_status", "payload": payload})


def main() -> None:
    init_db()

    client = mqtt.Client(client_id=CLIENT_ID_GUI, clean_session=True)
    client.on_connect = on_connect
    client.on_message = on_message

    print("[GUI] Starting GUI...")
    client.connect(BROKER_HOST, BROKER_PORT, MQTT_KEEPALIVE)
    client.loop_start()

    root = tk.Tk()
    app = SmartHomeGUI(root)
    app.client = client

    def on_close():
        client.loop_stop()
        client.disconnect()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()