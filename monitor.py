import logging
import os
import io
import time
import pprint
from dotenv import load_dotenv
import requests
import threading
from PIL import Image, ImageTk
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import plotly.graph_objects as go
from pymongo import MongoClient
from datetime import datetime

class ScheduleSettingWindow(ctk.CTkToplevel):
    """A window for setting schedules for a specific device."""
    
    def __init__(self, ip_address):
        super().__init__()
        self.ip_address = ip_address
        self.initialize_window()
        self.setup_ui()

    def initialize_window(self):
        """Initialize window properties."""
        self.title(f"Scheduling for {self.ip_address}")
        self.attributes("-topmost", True)

    def setup_ui(self):
        """Set up the user interface components for the scheduling window."""
        self.setup_main_layout()
        self.setup_create_schedule_section()
        self.setup_delete_schedule_section()
        self.setup_list_schedules_button()
        self.setup_schedules_display()

    def setup_main_layout(self):
        """Set up the main layout frames and global settings."""
        self.main_frame = ctk.CTkFrame(self, border_color='#1f538d', border_width=1)
        self.main_frame.grid(sticky="nsew")
        label = ctk.CTkLabel(self.main_frame, text="Scheduling")
        label.grid(row=0, column=0, columnspan=3, pady=10)
        self.grid_columnconfigure(0, weight=1)  # Make the main frame expandable

    def setup_create_schedule_section(self):
        """Set up UI components for creating schedules."""
        create_frame = ctk.CTkFrame(self.main_frame, border_width=1)
        create_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        self.setup_time_input(create_frame, "Day", 1, 0, "1-7")
        self.setup_time_input(create_frame, "Hour", 1, 1, "0-23")
        self.setup_time_input(create_frame, "Minute", 1, 2, "0-59")

        create_button = ctk.CTkButton(create_frame, text="Create", command=self.create_schedule)
        create_button.grid(row=3, column=1, padx=5, pady=5)

    def setup_time_input(self, frame, label_text, row, column, placeholder_text):
        """Create label and entry for time input in the schedule creation section."""
        label = ctk.CTkLabel(frame, text=f"{label_text}:")
        label.grid(row=row, column=column, padx=5, pady=5)
        entry = ctk.CTkEntry(frame, placeholder_text=placeholder_text)
        entry.grid(row=row + 1, column=column, padx=5, pady=5)
        setattr(self, f"{label_text.lower()}_entry", entry)

    def setup_delete_schedule_section(self):
        """Set up UI components for deleting schedules."""
        delete_frame = ctk.CTkFrame(self.main_frame, border_width=1)
        delete_frame.grid(row=1, column=3, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(delete_frame, text="Schedule Deletion").grid(row=0, padx=5, pady=5)
        self.schedule_id_entry = ctk.CTkEntry(delete_frame, placeholder_text="JOB ID# of Schedule")
        self.schedule_id_entry.grid(row=1, padx=5, pady=5)

        delete_button = ctk.CTkButton(delete_frame, text="Delete Schedule", command=self.delete_schedule)
        delete_button.grid(row=2, padx=5, pady=5)

    def setup_list_schedules_button(self):
        """Set up the button to list all schedules."""
        list_button = ctk.CTkButton(self.main_frame, text="List Schedules", command=self.list_schedules)
        list_button.grid(row=0, column=3, padx=5, pady=5)

    def setup_schedules_display(self):
        """Set up the display area for listing schedules."""
        self.schedule_text = ctk.CTkTextbox(self.main_frame, width=500, height=100)
        self.schedule_text.grid(row=5, column=0, columnspan=4, padx=5, pady=5)

    def list_schedules(self):
        """Fetches and displays a list of all schedules from the device."""
        self.schedule_text.delete("1.0", "end")  # Clear existing text
        try:
            response = requests.get(f"http://{self.ip_address}/rpc/Schedule.List", timeout=10)
            data = response.json()
            self.schedule_text.insert("end", "List of schedules:\n")
            for job in data.get('jobs', []):  # Safely handle missing jobs
                job_details = f"Job ID: {job.get('id', 'N/A')}, Enable: {job.get('enable', 'N/A')}, "
                job_details += f"Timespec: {job.get('timespec', 'N/A')}, Method: {job.get('calls', [{}])[0].get('method', 'N/A')}\n"
                self.schedule_text.insert("end", job_details)
        except requests.RequestException as e:
            CTkMessagebox(title="Error", message=f"Failed to list schedules: {e}")

    def create_schedule(self):
        """Creates a schedule based on user input for day, hour, and minute."""
        try:
            day, minute, hour = self.day_entry.get(), int(self.minute_entry.get()), int(self.hour_entry.get())
            timespec = f"0 {minute} {hour} * * {day}"
            params = '{"method":"switch.toggle","params":{"id":0}}'
            url = f"http://{self.ip_address}/rpc/Schedule.Create?timespec={timespec}&calls=[{params}]"
            print(url)
            response = requests.get(url, timeout=10)
            data = response.json()
            if 'code' in data and data['code'] == -103:
                CTkMessagebox(title="Error", message=f"Failed to create schedule: {data.get('message', 'Unknown error')}")
                logging.error(f"Failed to create schedule. {data.get('message', 'Unknown error')}")
            else:
                CTkMessagebox(title="Success", message="The schedule has been created successfully!")
        except ValueError:
            CTkMessagebox(title="Error", message="Failed to create a schedule: Please ensure all inputs are numbers.")
            logging.error("Failed to create schedule due to invalid input.")

    def delete_schedule(self):
        """Deletes a schedule based on the provided schedule ID."""
        try:
            schedule_id = int(self.schedule_id_entry.get())
            response = requests.get(f"http://{self.ip_address}/rpc/Schedule.Delete?id={schedule_id}", timeout=10)
            data = response.json()
            if 'code' in data and data['code'] == -103:
                CTkMessagebox(title="Warning", message="No schedule found with that ID.")
            else:
                CTkMessagebox(title="Success", message="Schedule deleted successfully!")
        except ValueError:
            CTkMessagebox(title="Error", message="Please enter a valid schedule ID number.")

class MonitoringApp(ctk.CTk):
    """A monitoring application for controlling and monitoring devices."""
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_logging()
        self.read_credentials()

    def setup_ui(self):
        """Set up the user interface of the application."""
        self.title("Device Monitoring")
        self.setup_main_frame()
        self.setup_tab_view()
        self.initialize_data_containers()
        self.configure_dark_mode()

    def setup_main_frame(self):
        """Create and configure the main frame of the application."""
        self.main_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", border_width=1, border_color='#1f538d')
        self.main_frame.grid(row=0, column=0, sticky='nsew')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def setup_tab_view(self):
        """Create and configure the tab view in the main frame."""
        self.tab_view = ctk.CTkTabview(self.main_frame, fg_color="black", border_width=1, border_color='#1f538d')
        self.tab_view.grid(row=0, column=0, sticky='nsew')
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

    def initialize_data_containers(self):
        """Initialize containers for status labels, text areas, and gauge labels."""
        self.status_labels = {}
        self.text_areas = {}
        self.gauge_labels = {}

    def configure_dark_mode(self):
        """Configure the application's appearance mode and color theme."""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

    def setup_logging(self):
        """Set up logging for the application."""
        logging.basicConfig(filename='monitoring.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

    def read_credentials(self):
        """Read device IP addresses from the .env file and create tabs for each."""
        load_dotenv()
        ip_addresses = [os.getenv(f'IP_ADDRESS_{i}') for i in range(1, 100) if os.getenv(f'IP_ADDRESS_{i}')]

        if not ip_addresses:
            self.display_no_ip_warning()
        else:
            for ip_address in ip_addresses:
                self.create_tab(ip_address)

    def display_no_ip_warning(self):
        """Display a warning message and log if no IP addresses are found."""
        logging.error("No IP address found in .env file.")
        CTkMessagebox(title="Error", message="No IP addresses found in the .env file.")

    def create_tab(self, ip_address):
        """Create a new tab for the given IP address and initialize its content."""
        tab = self.tab_view.add(ip_address)
        main_frame = self.setup_tab_main_frame(tab)
        self.setup_status_label(ip_address, main_frame)
        self.setup_text_areas(ip_address, main_frame)
        self.setup_gauge_labels(ip_address, main_frame)
        self.setup_control_buttons(ip_address, main_frame)
        self.update_data(ip_address)

    def setup_tab_main_frame(self, tab):
        """Create and configure the main frame within a tab."""
        main_frame = ctk.CTkFrame(tab)
        main_frame.grid(row=0, column=0, sticky='nsew')
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        return main_frame

    def setup_status_label(self, ip_address, main_frame):
        """Initialize and place the status label for the given IP address."""
        if ip_address not in self.status_labels:
            self.status_labels[ip_address] = ctk.CTkButton(main_frame, text="Status: Unknown", fg_color="transparent", hover="disabled", border_width=1, border_color="#1f538d", command=lambda addr=ip_address: self.toggle_switch(addr))
        self.status_labels[ip_address].grid(row=0, column=2, rowspan=3, sticky='nsew', pady=5, padx=5)

    def setup_text_areas(self, ip_address, main_frame):
        """Initialize and place text areas for device data for the given IP address."""
        if ip_address not in self.text_areas:
            self.text_areas[ip_address] = {}
        text_area_frame = ctk.CTkFrame(main_frame, border_width=1)
        text_area_frame.grid(row=1, column=0, pady=5, padx=5, sticky='nsew')
        self.populate_text_areas(ip_address, text_area_frame)

    def populate_text_areas(self, ip_address, frame):
        """Create and grid text areas and labels for different types of device data."""
        labels = ["Watts", "Volts", "Amps", "WattHours (Total Wh)", "Temp (F)"]
        for i, label in enumerate(labels):
            label_widget = ctk.CTkLabel(frame, text=f"{label}:", fg_color="#333", corner_radius=6)
            label_widget.grid(row=0, column=i, sticky='nsew', padx=5, pady=5)
            text_area = ctk.CTkLabel(frame, text="", width=133, corner_radius=6, fg_color="black")
            text_area.grid(row=1, column=i, sticky='nsew', padx=5, pady=5)
            self.text_areas[ip_address][label] = text_area

    def setup_gauge_labels(self, ip_address, main_frame):
        """Initialize and place gauge labels for the given IP address."""
        if ip_address not in self.gauge_labels:
            self.gauge_labels[ip_address] = {}
        gauge_frame = ctk.CTkFrame(main_frame, border_width=1)
        gauge_frame.grid(row=3, column=0, pady=5, padx=5, sticky='nsew')
        gauge_title = ctk.CTkButton(gauge_frame, text="Live Monitoring", fg_color="transparent", anchor="center", border_width=1, border_color="#1f538d", state="disabled", text_color_disabled="white")
        gauge_title.grid(row=1, column=0, sticky="s", columnspan=3, rowspan=1, padx=5)
        self.populate_gauge_labels(ip_address, gauge_frame)

    def populate_gauge_labels(self, ip_address, frame):
        """Create and grid labels for different types of gauges."""
        gauge_types = ["Power (W)", "Current (A)", "Voltage (V)"]
        for i, gauge_type in enumerate(gauge_types):
            gauge_label = ctk.CTkLabel(frame, text=gauge_type)
            gauge_label.grid(row=0, column=i, sticky='nsew', padx=5, pady=5)
            self.gauge_labels[ip_address][gauge_type] = gauge_label

    def setup_control_buttons(self, ip_address, main_frame):
        """Initialize and place control buttons for device operations."""
        schedule_button = ctk.CTkButton(main_frame, text="Set Schedule", command=lambda addr=ip_address: self.open_schedule_window(addr))
        schedule_button.grid(row=0, column=0, pady=5, padx=5, sticky='nsew')

        # Frame for plotting history
        history_frame = ctk.CTkFrame(main_frame, border_width=1)
        history_frame.grid(row=3, column=2, pady=5, padx=5, sticky='nsew', columnspan=1)

        plot_label = ctk.CTkLabel(history_frame, text="History")
        plot_label.grid(row=0, column=0, pady=5, padx=5, sticky="nsew", columnspan=2)

        # Entry for choosing from date
        fd_entry_label = ctk.CTkLabel(history_frame, text="FROM:")
        fd_entry_label.grid(row=1, column=0, pady=5, padx=5, sticky="nse")

        fd_entry = ctk.CTkEntry(history_frame, placeholder_text="YYYY_MM_DD")
        fd_entry.grid(row=1, column=1, pady=5, padx=5, sticky='nsew')

        # Entry for choosing to date
        td_entry_label = ctk.CTkLabel(history_frame, text="TO:")
        td_entry_label.grid(row=2, column=0, pady=5, padx=5, sticky="nse")

        td_entry = ctk.CTkEntry(history_frame, placeholder_text="YYYY_MM_DD")
        td_entry.grid(row=2, column=1, pady=5, padx=5, sticky='nsew')

        # Dropdown for choosing data type
        data_type_label = ctk.CTkLabel(history_frame, text="Data Type:")
        data_type_label.grid(row=3, column=0, pady=5, padx=5, sticky="nse")

        combobox = ctk.CTkComboBox(history_frame,
                                   values=["voltage", "current", "apower"],
                                   dropdown_fg_color="#1a1a1a")
        combobox.grid(row=3, column=1, pady=5, padx=5)

        # Button for additional action 1
        button2 = ctk.CTkButton(history_frame, text="Select Data Type", command=lambda: self.button_action(ip_address, fd_entry.get(), combobox.get()))
        button2.grid(row=4, column=0, pady=5, padx=5, sticky='nsew', columnspan=2)

    def format_ip_address(self, ip_address):
        return ip_address.replace('.', '_')


    def button_action(self, ip_address, fd_value, combo_value):
        # Convert the IP address format and other initial setup
        formatted_ip = self.format_ip_address(ip_address)

        try:
            # Attempt to connect to the MongoDB database
            client = MongoClient('localhost', 27017)
            db = client[formatted_ip]
            collection_name = str(fd_value)
            collection = db[collection_name]

            # Execute the query to retrieve all documents in the collection
            query_result = collection.find({})
            results_found = False

            for doc in query_result:
                if combo_value in doc:
                    # Print the document's relevant field value
                    pprint.pprint({combo_value: doc[combo_value]})
                    results_found = False
                else:
                    pprint.pprint({"Message": f"Document does not contain the field '{combo_value}'"})

            if not results_found:
                print("No documents found in the collection")

        except Exception as e:
            print(f"An error occurred: {e}")

    def toggle_switch(self, ip_address):
        """Toggle the switch of a device and update the status label."""
        try:
            response = self.send_device_command(ip_address, "Switch.Toggle")
            self.update_status_label_after_toggle(ip_address, response)
        except requests.RequestException as e:
            self.handle_request_exception(ip_address, e)

    def send_device_command(self, ip_address, command, retries=3):
        """Send a command to the device and return the response, with retries."""
        url = f"http://{ip_address}/rpc/{command}?id=0"
        for attempt in range(retries):
            try:
                return requests.get(url, timeout=10)
            except requests.RequestException as e:
                if attempt < retries - 1:  # If not the last attempt, wait and then try again
                    time.sleep(1)  # Wait for 1 seconds before retrying
                    continue
                else:  # If the last attempt also fails, log the error and raise the exception
                    logging.error(f"Error fetching data for {ip_address}: {e}")
                    raise

    def update_status_label_after_toggle(self, ip_address, response):
        """Update the status label based on the toggle switch response."""
        if '{"was_on":false}' in response.text:
            self.status_labels[ip_address].configure(text="OUTLET POWER IS ON", fg_color="green")
        elif '{"was_on":true}' in response.text:
            self.status_labels[ip_address].configure(text="OUTLET POWER IS OFF", fg_color="red")

    def update_switch_status(self, ip_address):
        """Update the switch status label based on the device's current state."""
        try:
            response = self.send_device_command(ip_address, "Switch.GetStatus")
            is_on = response.json().get("output", False)  # Get the 'output' value, default to False if not found
            self.status_labels[ip_address].configure(text="OUTLET POWER IS ON" if is_on else "OUTLET POWER IS OFF")
            color = "green" if is_on else "red"
            self.status_labels[ip_address].configure(text=text, fg_color=color)
        except requests.RequestException as e:
            self.handle_request_exception(ip_address, e)

    def open_schedule_window(self, ip_address):
        """Open the schedule setting window for the given IP address."""
        ScheduleSettingWindow(ip_address)
        pass

    def update_data(self, ip_address):
        """Fetch and display new data for the given IP address."""
        def fetch_data():
            try:
                response = self.send_device_command(ip_address, "Switch.GetStatus")
                if response.status_code == 200:
                    self.process_device_data(ip_address, response.json())
            except requests.RequestException as e:
                self.handle_request_exception(ip_address, e)
                # Re-schedule the update after a delay if there's an error
                self.after(5000, lambda: self.update_data(ip_address))

        # Start fetching data in a new thread
        thread = threading.Thread(target=fetch_data)
        thread.daemon = True  # Daemonize thread
        thread.start()

    def process_device_data(self, ip_address, data):
        """Process and display device data."""
        # Define default metrics to be used if data fetch fails or is incomplete
        default_metrics = {
            "Watts": 0,
            "Volts": 0,
            "Amps": 0,
            "WattHours (Total Wh)": 0,
            "Temp (F)": 0
        }

        if data:  # If there's valid data, update accordingly
            device_metrics = {
                "Watts": data.get("apower", 0),
                "Volts": data.get("voltage", 0),
                "Amps": data.get("current", 0),
                "WattHours (Total Wh)": data.get("aenergy", {}).get('total', 0),
                "Temp (F)": data.get("temperature", {}).get('tF', 0)
            }
        else:  # If data is missing or fetch failed, use default metrics
            device_metrics = default_metrics

        self.update_text_areas_with_data(ip_address, device_metrics)
        self.update_status_label_from_data(ip_address, data if data else {})
        self.update_gauge_charts(ip_address, device_metrics["Watts"], device_metrics["Amps"], device_metrics["Volts"])
        self.schedule_data_update(ip_address)

    def update_text_areas_with_data(self, ip_address, metrics):
        """Update the text areas with new device metrics."""
        for metric, value in metrics.items():
            value_label = self.text_areas[ip_address][metric]
            value_label.configure(text=str(value))

    def update_status_label_from_data(self, ip_address, data):
        """Update the status label based on the device's power status."""
        is_on = data.get("output", False)
        color = "green" if is_on else "red"
        self.status_labels[ip_address].configure(text="OUTLET POWER IS ON" if is_on else "OUTLET POWER IS OFF", fg_color=color)

    def update_gauge_charts(self, ip_address, power, current, voltage):
        """Update gauge charts with the latest data."""
        gauges = {
            "Power (W)": (power, 2000),
            "Current (A)": (current, 20),
            "Voltage (V)": (voltage, 240)
        }
        for gauge_type, (value, max_value) in gauges.items():
            self.update_gauge_chart(value, self.gauge_labels[ip_address][gauge_type], gauge_type, max_value)

    def update_gauge_chart(self, value, label, title, max_value):
        """Update a single gauge chart."""
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            title={'text': title, 'font': {'color': 'white', 'size': 36}, 'align': 'left'},
            gauge={
                'axis': {'range': [None, max_value], 'showticklabels': True, 'tickcolor': "white", 'tickfont': {'color': 'white', 'size': 16}},
                'bar': {'color': "#1f538d"},
                'bgcolor': "#333333",
                'steps': [{'range': [0, max_value * 0.5], 'color': "lightgray"}, {'range': [max_value * 0.5, max_value], 'color': "gray"}],
                'threshold': {'line': {'color': "black", 'width': 2}, 'thickness': 1, 'value': value}
            },
            number={'font': {'color': 'white', 'size': 75}}
        ))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin={'t': 20, 'b': 20, 'l': 50, 'r': 50})
        self.display_gauge_chart(fig, label)

    def display_gauge_chart(self, fig, label):
        """Display the gauge chart on the specified label."""
        label.configure(text="")  # Clear previous text
        img_bytes = fig.to_image(format="png")
        img = Image.open(io.BytesIO(img_bytes))
        img_tk = ctk.CTkImage(dark_image=img, size=(230,147))
        label.configure(image=img_tk)
        label.image = img_tk  # Keep a reference to avoid garbage collection

    def schedule_data_update(self, ip_address):
        """Schedule the next data update for the given IP address."""
        self.after(1000, lambda: self.update_data(ip_address))

    def set_device_data_to_zero(self, ip_address):
        # Set text areas to zero
        for metric in self.text_areas[ip_address]:
            text_area = self.text_areas[ip_address][metric]
            text_area.delete("1.0", "end")
            text_area.insert("1.0", "0")
        # Set gauge labels or charts to zero or clear them
        for gauge_type in self.gauge_labels[ip_address]:
            # This part depends on how you want to represent a disconnected state in your gauges.
            # For simplicity, you might just update the label, but you could also update the gauge charts themselves.
            self.gauge_labels[ip_address][gauge_type].configure(text=f"{gauge_type}: 0")

    def handle_request_exception(self, ip_address, e):
        """Log and display errors encountered when fetching data for a device."""
        logging.error(f"Error fetching data for {ip_address}: {e}")
        # Set UI elements to show '0' or 'Disconnected' or similar
        self.set_device_data_to_zero(ip_address)
        self.status_labels[ip_address].configure(text="Disconnected", fg_color="grey")


if __name__ == "__main__":
    app = MonitoringApp()
    app.mainloop()
