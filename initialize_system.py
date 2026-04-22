import sqlite3

DB_NAME = 'power_data.db'

def initialize_system():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Device Registry: Stripped down to only the functional hash
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT UNIQUE,
            credentials_hash TEXT,
            location_label TEXT,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    # Power Logs: Tracking power, network health, and uptime
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS power_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            outlet_name TEXT,
            host TEXT,
            ssid TEXT,
            rssi INTEGER,
            state INTEGER,
            on_since TEXT,
            current_w REAL,
            today_kwh REAL,
            month_kwh REAL
        )
    ''')
    conn.commit()
    conn.close()
    print(f"System initialized. {DB_NAME} is ready.")

if __name__ == "__main__":
    initialize_system()
