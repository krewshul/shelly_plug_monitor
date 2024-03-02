# Shelly Smart Plug US Monitoring and Scheduling App

### This application allows users to monitor and control their Shelly Smart Plug US devices remotely.

*Features:*

- [x] **Device Monitoring:** View real-time data such as power consumption, voltage, current, and temperature for each connected device.

- [x] **Remote Control:** Toggle the power state of devices on or off remotely from the application interface.

- [x] **Schedule Management:** Create, view, and delete schedules for automated tasks, such as turning devices on or off at specified times.

- [x] **Data Visualization:** Visualize power consumption trends over time.

- [x] **Error Handling:** Provides informative error messages and logs to help troubleshoot and resolve issues.

- [x] **User-Friendly Interface:** Intuitive user interface with tabbed layout for easy navigation and management of multiple devices.

*Requirements*

- Python 3.x

- Customtkinter (for GUI)

- CTkMessagebox (for error handling)

- requests (for making HTTP requests)

- plotly (for data visualization)

- kaleido (for data visualization)

- python-dotenv (to store environment variables)

*Download and run:*

`git clone https://github.com/krewshul/shelly_plug_monitor.git`

`cd shelly_plug_monitor`

`python -m virtualenv .`

- if on Windows `. Scripts\activate`
- if on Mac or Linux `. bin/activate`
  
`pip install -r requirements.txt`

- to start the app

`python start.py`

Upon launching the application, you'll be prompted with 2 buttons: "Set Credentials" and "Begin Monitoring"

1. Select "Set Credentials" and set your user name and the IP's of your devices. ***Currently username and password are not used. This will be implemented at a later date.***
   
2. After setting your credentials, press "Begin Monitoring" to start monitoring your devices.
   
Once the credentials are set and monitoring begun, the application will display the devices and their status. You can interact with each device, view real-time data, and schedule automated tasks as needed.

Use the buttons provided to toggle device power, create new schedules, view existing schedules, and chart power consumption trends.
