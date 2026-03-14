import sqlite3
from app.config import DB_PATH


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device TEXT NOT NULL,
            value REAL NOT NULL,
            unit TEXT,
            timestamp TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actuator_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            actuator TEXT NOT NULL,
            action TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def insert_sensor_data(device: str, value: float, unit: str, timestamp: str, status: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sensor_data (device, value, unit, timestamp, status)
        VALUES (?, ?, ?, ?, ?)
    """, (device, value, unit, timestamp, status))

    conn.commit()
    conn.close()


def insert_actuator_event(actuator: str, action: str, timestamp: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO actuator_events (actuator, action, timestamp)
        VALUES (?, ?, ?)
    """, (actuator, action, timestamp))

    conn.commit()
    conn.close()


def insert_system_log(level: str, message: str, timestamp: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO system_logs (level, message, timestamp)
        VALUES (?, ?, ?)
    """, (level, message, timestamp))

    conn.commit()
    conn.close()


def get_latest_sensor_value(device: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT value, unit, timestamp, status
        FROM sensor_data
        WHERE device = ?
        ORDER BY id DESC
        LIMIT 1
    """, (device,))

    row = cursor.fetchone()
    conn.close()
    return row


def get_latest_actuator_event(actuator: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT action, timestamp
        FROM actuator_events
        WHERE actuator = ?
        ORDER BY id DESC
        LIMIT 1
    """, (actuator,))

    row = cursor.fetchone()
    conn.close()
    return row


def get_recent_sensor_history(device: str, limit: int = 20):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, value, unit, status
        FROM sensor_data
        WHERE device = ?
        ORDER BY id DESC
        LIMIT ?
    """, (device, limit))

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_recent_actuator_history(actuator: str, limit: int = 20):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, action
        FROM actuator_events
        WHERE actuator = ?
        ORDER BY id DESC
        LIMIT ?
    """, (actuator, limit))

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_recent_system_logs(limit: int = 30):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, level, message
        FROM system_logs
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()
    return rows