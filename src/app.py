from flask import Flask, jsonify
import psutil
import csv
from datetime import datetime

app = Flask(__name__)

def log_metrics(cpu, ram):
    with open('metrics.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now(), cpu, ram])

@app.route('/health')
def health():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().available / (1024 * 1024)
    log_metrics(cpu, ram) # Logs every time you check
    return jsonify({
        "status": "online",
        "cpu_usage_percent": cpu,
        "ram_available_mb": round(ram, 2),
        "arch": "32-bit"
    })

if __name__ == '__main__':
    # '0.0.0.0' makes it accessible on your local WiFi
    app.run(host='0.0.0.0', port=5000)