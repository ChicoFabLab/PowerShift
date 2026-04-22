from flask import Flask, render_template, jsonify
import sqlite3

app = Flask(__name__)
DB_NAME = 'power_data.db'

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    db = get_db()
    # Get the latest row for each unique outlet name
    latest = db.execute('''
        SELECT outlet_name, timestamp, ssid, rssi, state, on_since, current_w, today_kwh, month_kwh 
        FROM power_logs 
        WHERE id IN (SELECT MAX(id) FROM power_logs GROUP BY outlet_name)
    ''').fetchall()
    return render_template('index.html', devices=latest)

@app.route('/api/history/<name>')
def history(name):
    db = get_db()
    # Pull last 100 entries for the graph
    rows = db.execute('''
        SELECT timestamp, current_w FROM power_logs 
        WHERE outlet_name = ? ORDER BY timestamp DESC LIMIT 100
    ''', (name,)).fetchall()
    return jsonify([{"time": r[0], "watts": r[1]} for r in reversed(rows)])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
  
