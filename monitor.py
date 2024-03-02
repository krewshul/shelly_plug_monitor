import logging
import os
import io
from dotenv import load_dotenv
import requests 
from PIL import Image
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import plotly.graph_objects as go

class ScheduleSettingWindow(ctk.CTkToplevel):
    """A window for setting schedules for a specific device."""
    def __init__(self, ip_address):
        super().__init__()
        self.ip_address = ip_address
        self.title(f"Scheduling for {ip_address}")
        self.setup_ui()
        self.attributes("-topmost", True)

    def setup_ui(self):
        main = ctk.CTkFrame(self, border_color='#1f538d', border_width=1)
        main.grid()
        label = ctk.CTkLabel(main, text="Create A Schedule")
        label.grid(row=0, column=0, columnspan=3, pady=10)
        ctk.set_appearance_mode("dark")  # Set this once in the main app instead if affecting the whole app
        ctk.set_default_color_theme("dark-blue")  # Set this once in the main app instead if affecting the whole app

        create_frame = ctk.CTkFrame(main, border_width=1)
        create_frame.grid(row=1, column=0, columnspan=3, rowspan=3, padx=5, pady=5, sticky="nsew")

        day_label = ctk.CTkLabel(create_frame, text="Day:")
        day_label.grid(row=1, column=0, padx=5, pady=5)

        self.day_entry = ctk.CTkEntry(create_frame, placeholder_text="1-7")
        self.day_entry.grid(row=2, column=0, padx=5, pady=5)

        hour_label = ctk.CTkLabel(create_frame, text="Hour:")
        hour_label.grid(row=1, column=1, padx=5, pady=5)
        self.hour_entry = ctk.CTkEntry(create_frame, placeholder_text="0-23")
        self.hour_entry.grid(row=2, column=1, padx=5, pady=5)

        minute_label = ctk.CTkLabel(create_frame, text="Minute:")
        minute_label.grid(row=1, column=2, padx=5, pady=5)
        self.minute_entry = ctk.CTkEntry(create_frame, placeholder_text="0-59")
        self.minute_entry.grid(row=2, column=2, padx=5, pady=5)

        delete_frame = ctk.CTkFrame(main, border_width=1)
        delete_frame.grid(row=1, column=3, rowspan=3, padx=5, pady=5, sticky="nsew")

        schedule_id_label = ctk.CTkLabel(delete_frame, text="Schedule Deletion")
        schedule_id_label.grid(row=0, column=0, padx=5, pady=5)
        self.schedule_id_entry = ctk.CTkEntry(delete_frame, placeholder_text="JOB ID# of Schedule")
        self.schedule_id_entry.grid(row=1, column=0, padx=5, pady=5)

        delete_button = ctk.CTkButton(delete_frame, fg_color="#1f538d", border_width=0, text="Delete Schedule", command=self.delete_schedule)
        delete_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        list_button = ctk.CTkButton(main, fg_color="#1f538d", border_width=0, text="List Schedules", command=self.list_schedules)
        list_button.grid(row=0, column=3, padx=5, pady=5)
        create_button = ctk.CTkButton(create_frame, fg_color="#1f538d", border_width=0, text="Create", command=self.create_schedule)
        create_button.grid(row=3, column=1, padx=5, pady=5)
        self.schedule_text = ctk.CTkTextbox(main, border_width=1)
        self.schedule_text.configure(width=500, height=100)
        self.schedule_text.grid(row=5, column=0, columnspan=4, padx=5, pady=5)

    def list_schedules(self):
        self.schedule_text.delete("1.0", "end")
        try:
            url = f"http://{self.ip_address}/rpc/Schedule.List"
            response = requests.get(url, timeout=10)
            data = response.json()
            self.schedule_text.insert("end", "List of schedules:\n")
            for job in data.get('jobs', []):
                job_id = job.get('id', '')
                enable = job.get('enable', '')
                timespec = job.get('timespec', '')
                calls_method = job.get('calls', [{}])[0].get('method', '')
                self.schedule_text.insert("end", f"Job ID: {job_id}, Enable: {enable}, Timespec: {timespec}, Method: {calls_method}\n")
        except requests.RequestException as e:
            CTkMessagebox(title="Error", message=f"Failed to list schedules: {e}")

    def create_schedule(self):
        try:
            day = self.day_entry.get()
            minute = int(self.minute_entry.get())
            hour = int(self.hour_entry.get())
            url = f"http://{self.ip_address}/rpc/Schedule.Create?timespec=0%20{minute}%20{hour}%20*%20*%20{day}&calls=[{{\"method\":\"switch.toggle\",\"params\":{{\"id\":0}}}}]"
            response = requests.get(url, timeout=10)
            data = response.json()
            if 'code' in data and data['code'] == -103:
                CTkMessagebox(title="Error", message=f"Failed to create a schedule: {data['message']}")
                logging.error(f"Failed to create schedule. {data['message']}")
            else:
                CTkMessagebox(title="Success", message="The schedule has been created!")
        except ValueError:
            CTkMessagebox(title="Error", message="Failed to create a schedule: Only use numbers to set a schedule")
            logging.error("Failed to create schedule. Only use numbers")
        except requests.RequestException as e:
            CTkMessagebox(title="Error", message=f"Failed to create a schedule: {e}")
            logging.error("Failed to create schedule")

    def delete_schedule(self):
        try:
            schedule_id = int(self.schedule_id_entry.get())
            url = f"http://{self.ip_address}/rpc/Schedule.Delete?id={schedule_id}"
            response = requests.get(url, timeout=10)
            data = response.json()
            if 'code' in data and data['code'] == -103:
                CTkMessagebox(title="Warning", message="No schedule is found with that ID")
            else:
                CTkMessagebox(title="Success", message="The schedule has been deleted!")
        except ValueError:
            CTkMessagebox(title="Error", message="Please enter the number of the schedule you wish to delete")

class MonitoringApp(ctk.CTk):
    """A monitoring application for controlling and monitoring devices."""
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_logging()
        self.read_credentials()

    def setup_ui(self):
        self.title("Device Monitoring")
        self.main_frame = ctk.CTkFrame(self, fg_color="black", border_width=1, border_color='#1f538d')
        self.main_frame.grid(row=0, column=0, sticky='nsew')  # Use grid instead of pack
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.tab_view = ctk.CTkTabview(self.main_frame, fg_color="black", border_width=1, border_color='#1f538d')
        self.tab_view.grid(row=0, column=0, sticky='nsew')  # Use grid instead of pack
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.status_labels = {}
        self.text_areas = {}
        self.gauge_labels = {}

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")


    def setup_logging(self):
        logging.basicConfig(filename='monitoring.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

    def read_credentials(self):
        load_dotenv()
        ip_addresses = [os.getenv(f'IP_ADDRESS_{i}') for i in range(1, 100) if os.getenv(f'IP_ADDRESS_{i}')]

        if not ip_addresses:
            self.display_no_ip_warning()
            logging.warning("No IP addresses found in .env file.")
        else:
            for ip_address in ip_addresses:
                self.create_tab(ip_address)

    def display_no_ip_warning(self):
        logging.error("No IP address found in .env file.")
        CTkMessagebox(title="Error", message="No IP address foound in the .env file")

    def create_tab(self, ip_address):
        tab = self.tab_view.add(ip_address)
        main_frame = ctk.CTkFrame(tab)
        main_frame.grid(row=0, column=0, sticky='nsew')  # Use grid instead of pack
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # Initialize status label for this IP address
        if ip_address not in self.status_labels:
            self.status_labels[ip_address] = ctk.CTkLabel(main_frame, text="Status: Unknown")
        self.status_labels[ip_address].grid(row=0, column=2, columnspan=1, sticky='nsew', pady=5, padx=5)

        # Initialize text areas for this IP address
        if ip_address not in self.text_areas:
            self.text_areas[ip_address] = {}
        text_area_frame = ctk.CTkFrame(main_frame, border_width=1)
        text_area_frame.grid(row=1, column=0, pady=5, padx=5, columnspan=1, sticky='nsew')
        labels = ["Watts", "Volts", "Amps", "Temp (C)", "Temp (F)"]
        for i, label in enumerate(labels):
            label_widget = ctk.CTkLabel(text_area_frame, text=label + ":")
            label_widget.grid(row=0, column=i, sticky='ew', padx=5, pady=5)
            text_area = ctk.CTkTextbox(text_area_frame, width=100, height=1)
            text_area.grid(row=1, column=i, sticky='ew', padx=5, pady=5)
            self.text_areas[ip_address][label] = text_area

        # Initialize gauge labels for this IP address
        if ip_address not in self.gauge_labels:
            self.gauge_labels[ip_address] = {}
        gauge_frame = ctk.CTkFrame(main_frame, border_width=1)
        gauge_frame.grid(row=3, column=0, columnspan=5, pady=5, padx=5, sticky='nsew')
        gauge_types = ["Power (W)", "Current (A)", "Voltage (V)"]
        for i, gauge_type in enumerate(gauge_types):
            gauge_image_label = ctk.CTkLabel(gauge_frame, text=gauge_type)
            gauge_image_label.grid(row=0, column=i, sticky='nsew', padx=5, pady=5)
            self.gauge_labels[ip_address][gauge_type] = gauge_image_label

        # Initialize schedule button for this IP address
        schedule_button = ctk.CTkButton(main_frame, text="Set Schedule", command=lambda addr=ip_address: self.open_schedule_window(addr))
        schedule_button.grid(row=0, column=0, columnspan=2, rowspan=1, pady=5, padx=5, sticky='nsew')

        # Initialize schedule button for this IP address
        toggle_button = ctk.CTkButton(main_frame, text="Toggle Power", command=lambda addr=ip_address: self.toggle_switch(addr), corner_radius=360)
        toggle_button.grid(row=1, column=2, columnspan=1, rowspan=2, pady=5, padx=5, sticky='nsw')
        
        # Update data and switch status initially for this IP address
        self.update_data(ip_address)
        self.update_switch_status(ip_address)

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

    def update_switch_status(self, ip_address):
        try:
            response = requests.get(f"http://{ip_address}/rpc/Switch.GetStatus?id=0", timeout=10)
            data = response.json()
            is_on = data.get("output", False)  # Get the 'output' value, default to False if not found
            self.status_labels[ip_address].configure(text="OUTLET POWER IS ON" if is_on else "OUTLET POWER IS OFF")
        except requests.RequestException as e:
            logging.error(f"Error getting switch status for {ip_address}: {e}")
            self.status_labels[ip_address].configure(text="Error fetching status")

    def open_schedule_window(self, ip_address):
        ScheduleSettingWindow(ip_address)

    def update_data(self, ip_address):
        try:
            response = requests.get(f"http://{ip_address}/rpc/Switch.GetStatus?id=0", timeout=10)
            if response.status_code == 200:
                data = response.json()
                apower = data.get("apower", "N/A")
                voltage = data.get("voltage", "N/A")
                current = data.get("current", "N/A")
                temp_c = data.get("temperature", {}).get('tC', 'N/A')
                temp_f = data.get("temperature", {}).get('tF', 'N/A')

                self.text_areas[ip_address]["Watts"].delete("1.0", "end")
                self.text_areas[ip_address]["Watts"].insert("1.0", str(apower))
                self.text_areas[ip_address]["Volts"].delete("1.0", "end")
                self.text_areas[ip_address]["Volts"].insert("1.0", str(voltage))
                self.text_areas[ip_address]["Amps"].delete("1.0", "end")
                self.text_areas[ip_address]["Amps"].insert("1.0", str(current))
                self.text_areas[ip_address]["Temp (C)"].delete("1.0", "end")
                self.text_areas[ip_address]["Temp (C)"].insert("1.0", str(temp_c))
                self.text_areas[ip_address]["Temp (F)"].delete("1.0", "end")
                self.text_areas[ip_address]["Temp (F)"].insert("1.0", str(temp_f))

                if data.get("output", False):
                    self.status_labels[ip_address].configure(text="OUTLET POWER IS ON")
                else:
                    self.status_labels[ip_address].configure(text="OUTLET POWER IS OFF")
                # Gauge chart update
                self.update_gauge_charts(ip_address, apower, current, voltage)
                self.after(1000, lambda: self.update_data(ip_address))

        except requests.RequestException as e:
            self.handle_request_exception(ip_address, e)

    def update_gauge_charts(self, ip_address, power, current, voltage):
        # Update gauge charts with the latest data
        gauges = {
            "Power (W)": (power, 2000),
            "Current (A)": (current, 20),
            "Voltage (V)": (voltage, 240)
        }
        for gauge_type, (value, max_value) in gauges.items():
            self.update_gauge_chart(value, self.gauge_labels[ip_address][gauge_type], gauge_type, max_value)

    def update_gauge_chart(self, value, label, title, max_value):
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            title={
                'text': title,
                'font': {'color': 'white', 'size': 36},
                'align': 'left'
            },

            gauge={
                'axis': {
                    'range': [None, max_value],
                    'showticklabels': True,
                    'tickcolor': "white",
                    'tickfont': {'color': 'white', 'size': 16},
                    },
                'bar': {'color': "#1f538d"},
                'bgcolor': "#333333",  # Background color of the gauge part
                'steps': [
                    {'range': [0, max_value * 0.5], 'color': "white"},
                    {'range': [max_value * 0.5, max_value], 'color': "white"}
                ],
                'borderwidth': 0,
                'threshold': {
                    'line': {'color': "black", 'width': 2},
                    'thickness': 1,
                    'value': value}
                },
                
            number={'font': {'color': 'white', 'size': 75}},
        ))

        # Set the overall background color of the plot
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
            plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
            margin={'t': 20, 'b': 20, 'l': 50, 'r': 50},  # Adjust margins to fit
        )

        # Clear the label's text before setting the image
        label.configure(text="")  # Set text to empty to remove any default or previous text

        img_bytes = fig.to_image(format="png")
        img = Image.open(io.BytesIO(img_bytes))

        img_tk = ctk.CTkImage(dark_image=img, size=(230, 160))
        label.configure(image=img_tk)
        label.image = img_tk  # Keep a reference to avoid garbage collection

    def handle_request_exception(self, ip_address, e):
        logging.error(f"Error fetching data for {ip_address}: {e}")
        self.status_labels[ip_address].configure(text="Error fetching data")


if __name__ == "__main__":
    logging.basicConfig(filename='monitoring.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
    app = MonitoringApp()
    app.mainloop()
