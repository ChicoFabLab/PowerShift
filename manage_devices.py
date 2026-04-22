import subprocess
import re
import sqlite3
import sys

DB_NAME = '/home/user/tapo-monitor/power_data.db'

def fetch_device_metadata(ip, user, pwd):
    """Temporary use of credentials to get the permanent hash and label."""
    # Updated to match your exact working command line
    cmd = ["kasa", "-v", "--host", ip, "--username", user, "--password", pwd, "--type", "smart"]
    
    try:
        # We increase timeout to 10s just in case the Pi is busy
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=10)
        out = result.stdout
        
        # Look for the first header, but skip "None" if that's what is returned
        label_match = re.search(r'==\s+(.*?)\s+\(.*\)\s+==', out)
        label = label_match.group(1).strip() if label_match else None
        
        # If the label is "None", we'll try to find the first Child name instead
        if not label or label == "None":
            child_match = re.search(r'==\s+([^=]+?)\s+\(P210M\)\s+==', out)
            label = child_match.group(1).strip() if child_match else f"Device-{ip}"

        # Extract the hash
        cred_hash = re.search(r'Credentials hash:\s+(.*)', out)
        
        return label, (cred_hash.group(1).strip() if cred_hash else None)
    except Exception as e:
        print(f"Handshake failed for {ip}: {e}")
        return None, None

def add_device(ip, user, pwd):
    label, cred_hash = fetch_device_metadata(ip, user, pwd)
    
    if not cred_hash:
        print("Failed to retrieve Credentials Hash. Check your username/password.")
        return

    conn = sqlite3.connect(DB_NAME)
    try:
        conn.execute('''
            INSERT INTO devices (ip_address, credentials_hash, location_label) 
            VALUES (?, ?, ?)
        ''', (ip, cred_hash, label))
        conn.commit()
        print(f"Successfully registered: {label}")
        print(f"IP: {ip}")
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

