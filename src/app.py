from flask import Flask, jsonify
import psutil
import csv
from datetime import datetime
import os
import time
import numpy as np
from collections import deque
import sqlite3

app = Flask(__name__)

last_ram = None
last_cleared = 0
ram_history = deque(maxlen=15)

def init_db():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    # Create table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS metrics
                 (timestamp DATETIME, cpu REAL, ram REAL, prediction TEXT)''')
    conn.commit()
    conn.close()


def predict_crash():
    if len(ram_history) < 10:
        return None # Need more data to be smart
    
    x = np.arange(len(ram_history))
    y = np.array(ram_history)

    slope, intercept = np.polyfit(x, y, 1)

    if slope < -0.1:
        critical_limit = 200 
        steps_to_crash = (critical_limit - intercept) / slope
        return round(steps_to_crash * 2, 1)
    return "stable" \


def analyze_trend(current_ram):
    global last_ram

    if last_ram is not None:
        diff = last_ram - current_ram
        if diff > 50:
            print(f"rapid ram loss ~{diff}")

    last_ram = current_ram


def log_metrics(cpu, ram, pred):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("INSERT INTO metrics VALUES (?, ?, ?, ?)", 
              (datetime.now(), cpu, ram, str(pred)))
    conn.commit()
    conn.close()


@app.route('/health')
def health():
    global ram_history
    global last_cleared

    current_time = time.time()
    cpu = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory().available / (1024 * 1024)
    percentage_used = psutil.virtual_memory().percent
    ram_history.append(ram)
    prediction = predict_crash()
    analyze_trend(ram)
    log_metrics(cpu, ram, prediction)

    if percentage_used >= 85 and (current_time - last_cleared) > 300:
        os.system('sync; echo 3 | sudo tee /proc/sys/vm/drop_caches')
        print("High Memory Cleared Caches")
        last_cleared = current_time

    return jsonify({
        "status": "online",
        "cpu_usage_percent": cpu,
        "ram_available_mb": round(ram, 2),
        "prediction_to_limit": prediction,
        "arch": "32-bit"
    })


@app.route('/history')
def history():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()
    return jsonify(rows)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)