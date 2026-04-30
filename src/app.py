from flask import Flask, jsonify
import psutil
import csv
from datetime import datetime
import os
import time


app = Flask(__name__)

last_ram = None
last_cleared = 0


def analyze_trend(current_ram):
    global last_ram

    if last_ram is not None:
        diff = last_ram - current_ram
        if diff > 50:
            print(f"rapid ram loss ~{diff}")

    last_ram = current_ram


def log_metrics(cpu, ram):
    with open('metrics.csv', 'a', buffering=1) as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now(), cpu, ram])


@app.route('/health')
def health():
    global last_cleared

    current_time = time.time()
    cpu = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory().available / (1024 * 1024)
    percentage_used = psutil.virtual_memory().percent

    analyze_trend(ram)
    log_metrics(cpu, ram)

    if percentage_used >= 85 and (current_time - last_cleared) > 300:
        os.system('sync; echo 3 | sudo tee /proc/sys/vm/drop_caches')
        print("High Memory Cleared Caches")
        last_cleared = current_time

    return jsonify({
        "status": "online",
        "cpu_usage_percent": cpu,
        "ram_available_mb": round(ram, 2),
        "arch": "32-bit"
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)