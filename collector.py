import subprocess
import re
import sqlite3
from datetime import datetime

DB_NAME = '/home/user/tapo-monitor/power_data.db'

def poll_all_devices():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Pulling only the IP and Hash
    cursor.execute("SELECT ip_address, credentials_hash FROM devices WHERE is_active = 1")
    rows = cursor.fetchall()
    
    now = datetime.now()

    for host, cred_hash in rows:
        cmd = ["kasa", "-v", "--host", host, "--credentials-hash", cred_hash, "--type", "smart", "device", "state"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            output = result.stdout

            # Parse Parent Network Data
            ssid_match = re.search(r'SSID \(ssid\): (.*)', output)
            rssi_match = re.search(r'RSSI \(rssi\): (-?\d+)', output)
            ssid = ssid_match.group(1).strip() if ssid_match else "Unknown"
            rssi = int(rssi_match.group(1)) if rssi_match else None

            # Split by Child Outlets
            sections = re.split(r'==\s+([\w\s]+)\s+\(.*\)\s+==', output)

            for i in range(1, len(sections), 2):
                name = sections[i].strip()
                data = sections[i+1]
                
                # Regex for health and consumption
                state_m = re.search(r'State \(state\): (True|False)', data)
                since_m = re.search(r'On since \(on_since\): ([\d\-\s\:]+)', data)
                curr_m = re.search(r'Current consumption.*: (\d+\.?\d*) W', data)
                today_m = re.search(r"Today's consumption.*: (\d+\.?\d*) kWh", data)
                month_m = re.search(r"This month's consumption.*: (\d+\.?\d*) kWh", data)

                if curr_m:
                    cursor.execute('''
                        INSERT INTO power_logs 
                        (timestamp, outlet_name, host, ssid, rssi, state, on_since, current_w, today_kwh, month_kwh)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (now, name, host, ssid, rssi, 
                          1 if state_m and state_m.group(1) == "True" else 0,
                          since_m.group(1) if since_m else None,
                          float(curr_m.group(1)), 
                          float(today_m.group(1)) if today_m else 0, 
                          float(month_m.group(1)) if month_m else 0))
            
            print(f"[{now.strftime('%H:%M:%S')}] Polled {host} ({ssid})")
        except Exception as e:
            print(f"Error polling {host}: {e}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    poll_all_devices()
