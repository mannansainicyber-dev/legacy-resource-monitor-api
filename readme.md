# Linux Resource Monitor & Remediation Service

A lightweight, distributed system for monitoring hardware performance and automating kernel-level memory management on resource-constrained 32-bit systems.

## Core Functionality

* **Remote Metrics API:** A Flask-based REST service that exposes real-time CPU and RAM utilization data.
* **Structured Data Persistence:** Migrated from flat-file CSV logging to an **SQLite3 database** to ensure data integrity and enable high-speed historical queries.
* **Automated System Remediation:** A background controller that monitors memory saturation and executes a synchronized kernel cache drop (`drop_caches`) when usage exceeds 85%.
* **Predictive Trend Analysis:** Uses Linear Regression to calculate a "Time-to-Limit" (TTL) metric based on a 15-point rolling window of memory consumption.

## Technical Architecture

* **Data Collection:** `psutil` interface for hardware-level abstraction.
* **Storage Layer:** SQLite3 for relational data storage with SQL injection prevention.
* **Networking:** Distributed Client-Server model using HTTP/JSON.
* **Optimization:** Implemented a Circular Buffer (`collections.deque`) to keep memory footprint static regardless of runtime duration.

## Usage

### 1. Database Initialization & Server Start
Running the server will automatically initialize the SQLite schema and start the API listener:
```bash
python3 src/app.py
```

### 2. API Endpoints
* **GET `/health`**: Returns current hardware stats, percentage used, and predicted seconds until memory exhaustion.
* **GET `/history`**: Returns the last 10 records from the SQL database in JSON format.

## System Integration

The project is designed to run as a persistent background daemon via `systemd`. This ensures the monitor starts on boot and restarts automatically in the event of a failure.

### Memory Management Logic
When the 85% threshold is crossed, the service executes a remediation sequence to prevent Out-Of-Memory (OOM) kills:
```python
os.system('sync; echo 3 | sudo tee /proc/sys/vm/drop_caches')
```
This forces the kernel to flush dirty pages to disk and free up pagecache, reclaiming available memory for active processes without requiring a system reboot.