import requests
import time
import os

LAPTOP_IP = input("ENTER IP OF SERVER: ")
URL = f"http://{LAPTOP_IP}:5000/health"

def fetch_metrics():
    try:
        response = requests.get(URL, timeout=2)
        if response.status_code == 200:
            data = response.json()
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print(f"=== REMOTE SENTINEL: {LAPTOP_IP} ===")
            print(f"Status:   {data['status'].upper()}")
            print(f"Arch:     {data['arch']}")
            print(f"CPU:      {data['cpu_usage_percent']}%")
            print(f"Free RAM: {data['ram_available_mb']} MB")
            print(f"prediction_to_limit: {data['prediction_to_limit']}")
            print("=====================================")
        else:
            print(f"Error: Server returned {response.status_code}")
    except Exception as e:
        print(f"Connection Failed: {e}")

if __name__ == "__main__":
    while True:
        fetch_metrics()
        time.sleep(2)