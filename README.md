# Shelly Smart Plug US Monitoring and Scheduling App

A desktop application for monitoring, controlling, and scheduling one or more Shelly Plus Plug US devices from a single interface.

The application provides real-time device telemetry, remote power control, automated scheduling, and live monitoring charts through a simple tabbed interface.

## Features

* [x] **Multi-Device Support**

  * Monitor and manage multiple Shelly Plus Plug US devices simultaneously.
  * Each device gets its own tab for easy navigation.

* [x] **Real-Time Monitoring**

  * View live device statistics including:

    * Power (Watts)
    * Voltage
    * Current
    * Temperature
    * Total Energy Usage (Watt Hours)

* [x] **Live Gauge Dashboard**

  * Dedicated gauges for:

    * Power Consumption
    * Current Draw
    * Voltage

* [x] **Historical Monitoring Charts**

  * Separate live charts for:

    * Watts
    * Amps
    * Volts
  * Automatically updates while monitoring.

* [x] **Remote Power Control**

  * Turn outlets on or off remotely.
  * Toggle outlet state directly from the device tab.

* [x] **Schedule Management**

  * Create scheduled toggle events.
  * View existing schedules.
  * Delete schedules.
  * Uses Shelly's built-in scheduling system.

* [x] **Error Handling**

  * Friendly error dialogs.
  * Logging to `monitoring.log` for troubleshooting.

* [x] **Persistent Configuration**

  * Device IP addresses are stored in a local `.env` file.
  * Automatically loaded the next time the application starts.

* [x] **Modern Interface**

  * Dark mode UI built with CustomTkinter.
  * Responsive layout.
  * Tabbed device management.

---

## Requirements

* Python 3.10+
* CustomTkinter
* CTkMessagebox
* requests
* python-dotenv
* matplotlib
* numpy
* pillow

---

## Installation

Clone the repository:

```bash
git clone https://github.com/krewshul/shelly_plug_monitor.git
cd shelly_plug_monitor
```

Create a virtual environment:

```bash
python -m venv .
```

Activate the virtual environment:

### Windows

```bash
.\Scripts\activate
```

### Linux / macOS

```bash
source bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the Application

Start the application:

```bash
python start.py
```

---

## Initial Setup

When the application launches, you will see three buttons:

### Add IP Address

Adds a new Shelly device entry.

Enter the local IP address of each Shelly Plus Plug US device you wish to monitor.

Examples:

```text
192.168.1.100
192.168.1.101
192.168.1.102
```

### Update

Saves all configured IP addresses to the `.env` file.

The IP list will be automatically restored the next time the application starts.

### Begin Monitoring

Launches the monitoring dashboard.

This button does **not** modify your saved configuration.

---

## Monitoring Dashboard

Each configured device receives its own tab.

Within each device tab you can:

### View Device Status

* Outlet ON/OFF status
* Last successful update timestamp

### Monitor Live Metrics

* Watts
* Volts
* Amps
* Watt Hours
* Temperature (°F)

### View Live Gauges

* Power Gauge
* Current Gauge
* Voltage Gauge

### View Historical Charts

Three dedicated charts are displayed:

* Power Usage (Watts)
* Current Draw (Amps)
* Voltage

Charts update automatically while monitoring.

### Control Device Power

* Turn On
* Turn Off
* Toggle by clicking the status button

### Manage Schedules

Create and manage Shelly schedules directly from the application.

Supported actions:

* Create Schedule
* View Schedule List
* Delete Schedule

---

## Notes

### Authentication

At this time, password-protected Shelly devices are not officially supported.

Monitoring generally works, but schedule management may fail on devices with authentication enabled.

If you are familiar with Shelly authentication and would like to contribute a solution, pull requests are welcome.

### Network Requirements

The application communicates directly with your Shelly devices using their local IP addresses.

Ensure:

* Your computer and Shelly devices are on the same network.
* Devices are reachable from your machine.
* Local firewall rules permit access.

---

## Logging

Errors and application events are written to:

```text
monitoring.log
```

This file can be useful when troubleshooting connectivity or scheduling issues.

---

## License

This project is open source and available under the MIT License.
