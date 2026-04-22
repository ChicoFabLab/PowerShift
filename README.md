# Local Power Monitoring System

A local-first, cloud-free telemetry system for monitoring TP-Link Tapo/Matter outlets (P210M) using the [python-kasa](https://github.com/python-kasa/python-kasa) CLI. This system logs power metrics and network health into a local SQLite database and serves a responsive web dashboard.

## 1. System Architecture
- Backend: Python 3 + SQLite3
- Hardware Interface: [python-kasa](https://github.com/python-kasa/python-kasa) (via --credentials-hash auth)
- Frontend: Flask + Chart.js
- Automation: System Cron

## 2. Prerequisites
Ensure your system is updated and has the necessary packages installed.

Command: sudo apt update && sudo apt install python3-pip sqlite3 -y

### Tapo App Settings
Before running any code, you must check this setting, or the plug will continue to reject your "challenge":

Open the Tapo App on your phone.

Go to Me (Profile) > Settings > Third-Party Compatibility.

Ensure this is set to ON.

Optional but recommended: Log into tplinkcloud.com and verify your password. If it contains complex symbols like & or #, consider changing it to a purely alphanumeric password, as these often cause "challenge mismatch" errors in Python.

## 3. Installation

1. Clone the project directory:

   Command: git clone https://github.com/ChicoFabLab/PowerShift.git tapo-monitor

3. Install [python-kasa](https://github.com/python-kasa/python-kasa):
   The collector relies on the kasa command-line utility.
   
   Command: pip install python-kasa --upgrade

5. Install Flask:

   Command: pip install flask

## 4. Setup & Configuration

### Step A: Initialize the Database
Run this script once to create power_data.db and the required tables for device registry and power logs.

Command: python3 initialize_system.py

### Step B: Register Devices
Run the management tool for each P210M outlet. This script handshakes with the device using your credentials, retrieves the Credentials Hash and Device Label, and saves only the hash to the database for future use.

Command: python3 manage_devices.py HOST USERNAME PASSWORD

### Step C: Secure the Database
To protect your credentials hashes, set restrictive file permissions:

Command: chmod 600 power_data.db

## 5. Automation (The Collector)
The collector.py script should be run every minute to capture a time-series record of your power usage.

1. Open the crontab editor:
   Command: crontab -e

2. Add the following line at the bottom (Replace 'user' with your actual Pi username):
   * * * * * /usr/bin/python3 /home/user/tapo-monitor/collector.py >> /home/user/tapo-monitor/collector.log 2>&1

## 6. Running the Web Dashboard
Start the Flask server to view your live graphs and network health metrics.

Command: python3 app.py

Access the dashboard at: http://<your-pi-ip>:5000

## 7. Captured Data Points
The system collects the following metrics every 60 seconds:
- Power: Current Watts, Today's kWh, Monthly kWh.
- Network: SSID and RSSI (Signal Strength).
- Uptime: 'On Since' timestamp for each outlet.
- State: Logical On/Off status.

---
Developed for local-first hardware monitoring at ChicoFabLab.
