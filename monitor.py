"""
App: monitor.py
Description: This will monitor your Shelly Smart Plug.
"""

import logging
import time
import os
from dotenv import load_dotenv
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import requests

class ScheduleSettingWindow(ctk.CTkToplevel):
    """A window for setting schedules for a specific device."""

    def __init__(self, ip_address):
        """Initialize the ScheduleSettingWindow.

        Args:
            ip_address (str): The IP address of the device.
        """
        super().__init__()
        self.ip_address = ip_address
        self.title(f"Scheduling for {ip_address}")
        self.setup_ui()
        self.attributes("-topmost", True)  # Set the window to be topmost


    def setup_ui(self):
        """Set up the user interface for schedule setting."""
        # Label to indicate the purpose of the window
        label = ctk.CTkLabel(self, text="Create A Schedule")
        label.grid(row=0, column=0, columnspan=3, pady=10)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Create a frame for the schedule creation
        create_frame = ctk.CTkFrame(self, fg_color="#333333")  # Gray background
        create_frame.grid(row=1, column=0, columnspan=3, rowspan=3, padx=5, pady=5, sticky="nsew")

        # Day Entry and Label
        day_label = ctk.CTkLabel(create_frame, text="Day:")
        day_label.grid(row=1, column=0, padx=5, pady=5)
        self.day_entry = ctk.CTkEntry(create_frame, placeholder_text="1-7")
        self.day_entry.grid(row=2, column=0, padx=5, pady=5)

        # Hour Entry and Label
        hour_label = ctk.CTkLabel(create_frame, text="Hour:")
        hour_label.grid(row=1, column=1, padx=5, pady=5)
        self.hour_entry = ctk.CTkEntry(create_frame, placeholder_text="0-23")
        self.hour_entry.grid(row=2, column=1, padx=5, pady=5)

        # Minute Entry and Label
        minute_label = ctk.CTkLabel(create_frame, text="Minute:")
        minute_label.grid(row=1, column=2, padx=5, pady=5)
        self.minute_entry = ctk.CTkEntry(create_frame, placeholder_text="0-59")
        self.minute_entry.grid(row=2, column=2, padx=5, pady=5)

        # Create a frame for the schedule ID entry and delete button
        delete_frame = ctk.CTkFrame(self, fg_color="#333333")  # Gray background
        delete_frame.grid(row=1, column=3, rowspan=3, padx=5, pady=5, sticky="nsew")

        # Schedule ID Entry and Label inside the frame
        schedule_id_label = ctk.CTkLabel(delete_frame, text="Schedule Deletion")
        schedule_id_label.grid(row=0, column=0, padx=5, pady=5)
        self.schedule_id_entry = ctk.CTkEntry(delete_frame, placeholder_text="JOB ID# of Schedule")
        self.schedule_id_entry.grid(row=1, column=0, padx=5, pady=5)

        # Delete Button inside the frame
        delete_button = ctk.CTkButton(delete_frame,
                                      fg_color="transparent",
                                      border_width=2,
                                      text="Delete Schedule",
                                      command=self.delete_schedule)
        delete_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # Buttons for schedule actions
        list_button = ctk.CTkButton(self,
                                    fg_color="transparent",
                                    border_width=2,
                                    text="List Schedules",
                                    command=self.list_schedules)
        list_button.grid(row=0, column=3, padx=5, pady=5)
        create_button = ctk.CTkButton(create_frame,
                                      fg_color="transparent",
                                      border_width=2,
                                      text="Create",
                                      command=self.create_schedule)
        create_button.grid(row=3, column=1, padx=5, pady=5)

        # Text widget to display the schedule data
        self.schedule_text = ctk.CTkTextbox(self)
        self.schedule_text.configure(width=500, height=100)

        self.schedule_text.grid(row=5, column=0, columnspan=5, padx=5, pady=5)

    def list_schedules(self):
        """List schedules for the device."""
        # Clear previous content
        self.schedule_text.delete("1.0", "end")

        # Listing schedules
        try:
            url = f"http://{self.ip_address}/rpc/Schedule.List"
            response = requests.get(url, timeout=10)
            data = response.json()

            # Display data in the text widget
            self.schedule_text.insert("end", "List of schedules:\n")
            for job in data.get('jobs', []):
                job_id = job.get('id', '')
                enable = job.get('enable', '')
                timespec = job.get('timespec', '')
                calls_method = job.get('calls', [{}])[0].get('method', '')
                self.schedule_text.insert("end",
                                          f"Job ID: {job_id}, Enable: {enable}, Timespec: {timespec}, Method: {calls_method}\n")
        except requests.RequestException as e:
            CTkMessagebox(title="Error!",
                          message=f"Failed to list schedules: {e}",
                          icon="error")

    def create_schedule(self):
        """Create a schedule for the device."""
        try:
            day = self.day_entry.get()
            minute = int(self.minute_entry.get())
            hour = int(self.hour_entry.get())

            url = f"http://{self.ip_address}/rpc/Schedule.Create?timespec=0%20{minute}%20{hour}%20*%20*%20{day}&calls=[{{\"method\":\"switch.toggle\",\"params\":{{\"id\":0}}}}]"
            response = requests.get(url, timeout=10)
            data = response.json()

            if 'code' in data and data['code'] == -103:
                CTkMessagebox(title="Error!",
                              message=f"Failed to create a schedule: {data['message']}",
                              icon="cancel")
                logging.error(f"Failed to create schedule. {data['message']}")

            else:
                CTkMessagebox(master=self.master,
                              title="Success!",
                              message="The schedule has been created!",
                              icon="info")
        except ValueError:
            CTkMessagebox(title="Error!",
                          message="Failed to create a schedule: Only use numbers to set a schedule",
                          icon="cancel")
            logging.error("Failed to create schedule. Only use numbers")
        except requests.RequestException as e:
            CTkMessagebox(title="Error!",
                          message=f"Failed to create a schedule: {e}",
                          icon="cancel")
            logging.error("Failed to create schedule")

    def delete_schedule(self):
        """Delete a schedule for the device."""
        try:
            schedule_id = int(self.schedule_id_entry.get())

            url = f"http://{self.ip_address}/rpc/Schedule.Delete?id={schedule_id}"
            response = requests.get(url, timeout=10)
            data = response.json()

            if 'code' in data and data['code'] == -103:
                CTkMessagebox(title="Error!",
                              message="No schedule is found with that ID",
                              icon="warning")
            else:
                CTkMessagebox(master=self.master,
                              title="Success!",
                              message="The schedule has been deleted!",
                              icon="info")
        except ValueError:
            CTkMessagebox(title="Error!",
                          message="Please enter the number of the schedule you wish to delete",
                          icon="cancel")

class MonitoringApp(ctk.CTk):
    """A monitoring application for controlling and monitoring devices."""

    def __init__(self):
        """Initialize the MonitoringApp."""
        super().__init__()
        self.setup_ui()
        self.setup_logging()
        self.read_credentials()

    def setup_ui(self):
        """Set up the user interface for the application."""
        # Sets appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.title("Devices")

        # Main frame and tab view
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)
        self.tab_view = ctk.CTkTabview(self.main_frame)
        self.tab_view.pack(fill="both", expand=True)
        self.status_labels = {}  # Dictionary to store status labels for each tab
        self.text_areas = {}  # Dictionary to store text areas for each tab

    def setup_logging(self):
        """Set up logging configuration."""
        # Configures logging to a file
        logging.basicConfig(filename='monitoring.log',
                            level=logging.ERROR,
                            format='%(asctime)s - %(levelname)s - %(message)s')

    def read_credentials(self):
        """Read device IP addresses from .env file and create tabs."""
        try:
            load_dotenv()  # Load variables from .env file
            ip_addresses = [os.getenv(f'IP_ADDRESS_{i}') for i in range(1, 100) if os.getenv(f'IP_ADDRESS_{i}')]

            if not ip_addresses:
                self.display_no_ip_warning()
                logging.warning("No IP addresses found in .env file.")
                return

            for ip_address in ip_addresses:
                self.create_tab(ip_address)
                self.update_data(ip_address)
        except Exception:
            CTkMessagebox(title="Error",
                          message=f"NOT COMMUNICATING WITH {ip_address}",
                          icon="cancel",
                          cancel_button="none",
                          button_color="transparent",
                          button_hover_color="gray13",
                          option_1=" ")
            logging.error(f"Failed to communicate with IP address {ip_address} from .env while opening the monitor.py")
            self.after(3000, self.quit)

    def display_no_ip_warning(self):
        """Display a warning when no IP addresses are found in credentials file."""
        message_label = ctk.CTkLabel(self.tab_view,
                                     text="Please set the IP addresses in your credentials file")
        message_label.pack(pady=20)

    def create_tab(self, ip_address):
        """Create a tab for a device with status labels and buttons."""
        tab = self.tab_view.add(ip_address)
        main_frame = ctk.CTkFrame(tab)
        main_frame.pack(fill="both", expand=True)
        status_label = ctk.CTkLabel(main_frame, text="STATUS")
        status_label.pack(pady=5)
        self.status_labels[ip_address] = status_label

        # Text areas for displaying device data
        text_area_frame = ctk.CTkFrame(main_frame)
        text_area_frame.pack(pady=5, padx=5)
        self.text_areas[ip_address] = {}

        labels = ["Watts", "Volts", "Amps", "Temp (C)", "Temp (F)"]
        for i, label in enumerate(labels):
            text_area_label = ctk.CTkLabel(text_area_frame, text=label + ": ")
            text_area_label.grid(row=0, column=i*2, sticky="e", padx=5, pady=5, ipadx=5, ipady=5)
            text_area = ctk.CTkTextbox(text_area_frame, width=75, height=1)
            text_area.grid(row=0, column=i*2+1, sticky="w", padx=5, pady=5)
            self.text_areas[ip_address][label] = text_area

        # Button to toggle switch
        toggle_button = ctk.CTkButton(tab,
                                      fg_color="transparent",
                                      border_width=2,
                                      text="Toggle",
                                      command=lambda addr=ip_address: self.toggle_switch(addr))
        toggle_button.pack(pady=5)

        # Button to open schedule setting window
        schedule_button = ctk.CTkButton(tab,
                                        fg_color="transparent",
                                        border_width=2,
                                        text="Set Schedule",
                                        command=lambda addr=ip_address: self.open_schedule_window(addr))
        schedule_button.pack(pady=5)

        # Button to chart power
        chart_button = ctk.CTkButton(tab,
                                     fg_color="transparent",
                                     border_width=2,
                                     text="Chart Power",
                                     command=lambda addr=ip_address: self.chart_power(addr))
        chart_button.pack(pady=5)

    def open_schedule_window(self, ip_address):
        """Open the schedule setting window for a specific device."""
        schedule_window = ScheduleSettingWindow(ip_address)
        schedule_window.lift() 

    def toggle_switch(self, ip_address):
        """Toggle the switch of a device and update the status label."""
        try:
            url = f"http://{ip_address}/rpc/Switch.Toggle?id=0"
            response = requests.get(url, timeout=10)

            if '{"was_on":false}' in response.text:
                self.status_labels[ip_address].configure(text="OUTLET POWER IS ON")
            elif '{"was_on":true}' in response.text:
                self.status_labels[ip_address].configure(text="OUTLET POWER IS OFF")

        except requests.RequestException as e:
            self.handle_request_exception(ip_address, e)

    def chart_power(self, ip_address):
        """Chart the power consumption of a device over time."""
        try:
            url = f"http://{ip_address}/rpc/Switch.GetStatus?id=0"

            # Initialize lists to store data
            apower_list = []  # List to store power consumption
            voltage_list = []  # List to store voltage
            current_list = []  # List to store current

            # Function to update the chart continuously
            def update_chart():
                try:
                    response = requests.get(url, timeout=10)
                    data = response.json()

                    apower = data.get("apower")
                    voltage = data.get("voltage")
                    current = data.get("current")

                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    timestamps.append(timestamp)

                    apower_list.append(apower)
                    voltage_list.append(voltage)
                    current_list.append(current)

                    if len(timestamps) > 12:
                        timestamps.pop(0)
                        apower_list.pop(0)
                        voltage_list.pop(0)
                        current_list.pop(0)

                    ax.clear()
                  
                    ax.plot(timestamps, apower_list, label="W", marker='x', linestyle='-')
                    ax.plot(timestamps, voltage_list, label="V", marker='+', linestyle=':')
                    ax.plot(timestamps, current_list, label="A", marker='o', linestyle='--')
                    
                    # Annotate each data point with its value
                    for i in range(len(timestamps)):
                        ax.annotate(f'{apower_list[i]:.2f}', (timestamps[i], apower_list[i]), textcoords="offset points", xytext=(0,10), ha='center')

                    # Annotate each data point with its value for voltage
                    for i in range(len(timestamps)):
                        ax.annotate(f'{voltage_list[i]:.2f}', (timestamps[i], voltage_list[i]), textcoords="offset points", xytext=(0,10), ha='center')

                    # Annotate each data point with its value for current
                    for i in range(len(timestamps)):
                        ax.annotate(f'{current_list[i]:.2f}', (timestamps[i], current_list[i]), textcoords="offset points", xytext=(0,10), ha='center')

                    ax.set_xlabel(" ")
                    ax.set_title(" ")
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(True)
                    ax.spines['bottom'].set_visible(True)
                    ax.spines['left'].set_visible(True)
                    ax.grid(False)
                    ax.figure.autofmt_xdate()
                    ax.set_facecolor('#333333')
                    
                    ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0., frameon=False)

                    canvas.draw()

                    self.after(5000, update_chart)

                except requests.RequestException as e:
                    error_msg = f"Error fetching data for {ip_address}: {e}"
                    CTkMessagebox(title="Error!",
                                  message=error_msg,
                                  icon="error")
                    logging.error(error_msg)

            chart_button = self.tab_view.tab(ip_address).winfo_children()[-1]
            chart_button.pack_forget()

            chart_frame = ctk.CTkFrame(self.tab_view.tab(ip_address))
            chart_frame.pack(fill="both")

            fig = Figure(figsize=(11, 4))
            ax = fig.add_subplot(211)
            fig.patch.set_facecolor('#212121')
            plt.style.use('dark_background')

            timestamps = []

            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.get_tk_widget().pack()

            fig.subplots_adjust(bottom=0.15)

            update_chart()

        except requests.RequestException as e:
            error_msg = f"Error fetching data for {ip_address}: {e}"
            CTkMessagebox(title="Error!",
                          message=error_msg,
                          icon="error")
            logging.error(error_msg)

    def update_data(self, ip_address):
        """Update the data for a device including power, voltage, current, and temperature."""
        try:
            url = f"http://{ip_address}/rpc/Switch.GetStatus?id=0"
            response = requests.get(url, timeout=10)

            data = response.json()

            apower = data.get("apower", "N/A")
            voltage = data.get("voltage", "N/A")
            current = data.get("current", "N/A")
            temperature = data.get("temperature", "N/A")

            self.update_ui(ip_address, response, apower, voltage, current, temperature)
            self.after(5000, lambda: self.update_data(ip_address))

        except requests.RequestException as e:
            self.handle_request_exception(ip_address, e)

    def update_ui(self, ip_address, response, apower, voltage, current, temperature):
        """Update the UI with the latest data for a device."""
        temp_c = temperature.get('tC', 'N/A')
        temp_f = temperature.get('tF', 'N/A')

        self.status_labels[ip_address].configure(text="STATUS")  # Update the status label
        
        # Update text areas
        for label, text_area in self.text_areas[ip_address].items():
            if label == "Watts":
                text_area.delete("1.0", "end")
                text_area.insert("1.0", apower)
            elif label == "Volts":
                text_area.delete("1.0", "end")
                text_area.insert("1.0", voltage)
            elif label == "Amps":
                text_area.delete("1.0", "end")
                text_area.insert("1.0", current)
            elif label == "Temp (C)":
                text_area.delete("1.0", "end")
                text_area.insert("1.0", temp_c)
            elif label == "Temp (F)":
                text_area.delete("1.0", "end")
                text_area.insert("1.0", temp_f)

        if '"output":true' in response.text:
            self.status_labels[ip_address].configure(text="OUTLET POWER IS ON")
        elif '"output":false' in response.text:
            self.status_labels[ip_address].configure(text="OUTLET POWER IS OFF")

    def handle_request_exception(self, ip_address, e):
        """Handle exceptions that occur during requests and log the errors."""
        error_msg = f"Error fetching data for {ip_address}: {e}"
        error_label = ctk.CTkLabel(self.tab_view, text=error_msg)
        error_label.pack(pady=20)
        logging.error(error_msg)

if __name__ == "__main__":
    app = MonitoringApp()
    app.mainloop()