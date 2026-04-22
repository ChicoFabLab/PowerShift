import subprocess
import re
import sqlite3
import sys

DB_NAME = 'power_data.db'

def fetch_device_metadata(ip, user, pwd):
    """Temporary use of credentials to get the permanent hash and label."""
    cmd = ["kasa", "-v", "--host", ip, "--username", user, "--password", pwd, "--type", "smart", "device", "state"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        out = result.stdout
        
        label = re.search(r'==\s+(.*?)\s+\(.*\)\s+==', out)
        cred_hash = re.search(r'Credentials hash:\s+(.*)', out)
        
        return (label.group(1).strip() if label else None, 
                cred_hash.group(1).strip() if cred_hash else None)
    except Exception as e:
        print(f"Handshake failed for {ip}: {e}")
        return None, None

def add_device(ip, user, pwd):
    label, cred_hash = fetch_device_metadata(ip, user, pwd)
    
    if not label or not cred_hash:
        print("Failed to retrieve device identity. Device not added.")
        return

    conn = sqlite3.connect(DB_NAME)
    try:
        conn.execute('''
            INSERT INTO devices (ip_address, credentials_hash, location_label) 
            VALUES (?, ?, ?)
        ''', (ip, cred_hash, label))
        conn.commit()
        print(f"Successfully registered: {label}")
        print(f"Auth Token: {cred_hash[:8]}...[HIDDEN]")
    except sqlite3.IntegrityError:
        print(f"Device at {ip} is already in the registry.")
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 manage_devices.py <IP> <USERNAME> <PASSWORD>")
    else:
        add_device(sys.argv[1], sys.argv[2], sys.argv[3])
