import requests
import logging
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import time

class ScheduleSettingWindow(ctk.CTkToplevel):
    def __init__(self, ip_address):
        super().__init__()
        self.ip_address = ip_address
        self.title(f"Scheduling for {ip_address}")
        self.setup_ui()

    def setup_ui(self):
        # Label to indicate the purpose of the window
        label = ctk.CTkLabel(self, text=f"Create A Schedule")
        label.grid(row=0, column=0, columnspan=3, pady=10)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Create a frame for the schedule creation
        create_frame = ctk.CTkFrame(self, fg_color="#333333")  # Gray background
        create_frame.grid(row=1, column=0, columnspan=3, rowspan=3, padx=5, pady=5, sticky="nsew")
        
        # Day Entry and Label
        day_label = ctk.CTkLabel(create_frame, text=f"Day:")
        day_label.grid(row=1, column=0, padx=5, pady=5)
        self.day_entry = ctk.CTkEntry(create_frame, placeholder_text="0-6")
        self.day_entry.grid(row=2, column=0, padx=5, pady=5)

        # Hour Entry and Label
        hour_label = ctk.CTkLabel(create_frame, text=f"Hour:")
        hour_label.grid(row=1, column=1, padx=5, pady=5)
        self.hour_entry = ctk.CTkEntry(create_frame, placeholder_text="0-23")
        self.hour_entry.grid(row=2, column=1, padx=5, pady=5)

        # Minute Entry and Label
        minute_label = ctk.CTkLabel(create_frame, text=f"Minute:")
        minute_label.grid(row=1, column=2, padx=5, pady=5)
        self.minute_entry = ctk.CTkEntry(create_frame, placeholder_text="0-59")
        self.minute_entry.grid(row=2, column=2, padx=5, pady=5)

        # Create a frame for the schedule ID entry and delete button
        delete_frame = ctk.CTkFrame(self, fg_color="#333333")  # Gray background
        delete_frame.grid(row=1, column=3, rowspan=3, padx=5, pady=5, sticky="nsew")

        # Schedule ID Entry and Label inside the frame
        schedule_id_label = ctk.CTkLabel(delete_frame, text=f"Schedule Deletion")
        schedule_id_label.grid(row=0, column=0, padx=5, pady=5)
        self.schedule_id_entry = ctk.CTkEntry(delete_frame, placeholder_text=f"JOB ID# of Schedule")
        self.schedule_id_entry.grid(row=1, column=0, padx=5, pady=5)

        # Delete Button inside the frame
        delete_button = ctk.CTkButton(delete_frame, fg_color="transparent", border_width=2, text=f"Delete Schedule", command=self.delete_schedule)
        delete_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # Buttons for schedule actions
        list_button = ctk.CTkButton(self, fg_color="transparent", border_width=2, text=f"List Schedules", command=self.list_schedules)
        list_button.grid(row=0, column=3, padx=5, pady=5)
        create_button = ctk.CTkButton(create_frame, fg_color="transparent", border_width=2, text=f"Create", command=self.create_schedule)
        create_button.grid(row=3, column=1, padx=5, pady=5)
        
        # Text widget to display the schedule data
        self.schedule_text = ctk.CTkTextbox(self)
        self.schedule_text.configure(width=500, height=100)

        self.schedule_text.grid(row=5, column=0, columnspan=5, padx=5, pady=5)

    # Method to list schedules
    def list_schedules(self):
        # Clear previous content
        self.schedule_text.delete("1.0", "end")

        # Listing schedules
        try:
            url = f"http://{self.ip_address}/rpc/Schedule.List"
            response = requests.get(url)
            data = response.json()

            # Display data in the text widget
            self.schedule_text.insert("end", "List of schedules:\n")
            for job in data.get('jobs', []):
                job_id = job.get('id', '')
                enable = job.get('enable', '')
                timespec = job.get('timespec', '')
                calls_method = job.get('calls', [{}])[0].get('method', '')
                self.schedule_text.insert("end", f"Job ID: {job_id}, Enable: {enable}, Timespec: {timespec}, Method: {calls_method}\n")
        except requests.RequestException as e:
            print(f"Error listing schedules: {e}")

    # Method to create a schedule
    def create_schedule(self):
        
        try:
            day = self.day_entry.get()
            minute = int(self.minute_entry.get())
            hour = int(self.hour_entry.get())
            
            url = f"http://{self.ip_address}/rpc/Schedule.Create?timespec=0%20{minute}%20{hour}%20*%20*%20{day}&calls=[{{\"method\":\"switch.toggle\",\"params\":{{\"id\":0}}}}]"
            response = requests.get(url)
            data = response.json()
            
            if 'code' in data and data['code'] == -103:
                CTkMessagebox(title="Error!", message=f"Failed to create a schedule: {data['message']}", icon="cancel")
            else:
                CTkMessagebox(master=self.master, title="Success!", message="The schedule has been created!", icon="check")
        except ValueError as e:
            CTkMessagebox(title="Error!", message=f"Failed to create a schedule: Only use numbers to set a schedule", icon="cancel")
        except requests.RequestException as e:
            CTkMessagebox(title="Error!", message=f"Failed to create a schedule: {e}", icon="cancel")

    # Method to delete a schedule
    def delete_schedule(self):

        try:
            schedule_id = int(self.schedule_id_entry.get())
            
            url = f"http://{self.ip_address}/rpc/Schedule.Delete?id={schedule_id}"
            response = requests.get(url)
            data = response.json()

            if 'code' in data and data['code'] == -103:
                CTkMessagebox(title="Error!", message="No schedule is found with that ID", icon="warning")
            else:
                CTkMessagebox(master=self.master, title="Success!", message="The schedule has been deleted!", icon="check")
        except ValueError as e:
            CTkMessagebox(title="Error!", message="Please enter the number of the schedule you wish to delete", icon="cancel")

class MonitoringApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_logging()
        self.read_credentials()

    def setup_ui(self):
        # Sets appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.title("Devices")

        # Main frame and tab view
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)
        self.tab_view = ctk.CTkTabview(self.main_frame)
        self.tab_view.pack(fill="both", expand=True)
        self.text_areas = {}  # Dictionary to store text areas for each tab
        self.status_labels = {}  # Dictionary to store status labels for each tab

    def setup_logging(self):
        # Configures logging to a file
        logging.basicConfig(filename='monitoring.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

    def read_credentials(self):
        # Reads IP addresses from a credentials file and creates tabs for each device
        try:
            with open("credentials.py", "r") as file:
                lines = file.readlines()

                ip_addresses = []
                for line in lines:
                    line = line.strip()
                    if line.startswith("IP_ADDRESS"):
                        variable_name, value = line.split("=")
                        ip_address = value.strip().strip("'\"")
                        ip_addresses.append(ip_address)

                if not ip_addresses:
                    self.display_no_ip_warning()
                    logging.warning("No IP addresses found in credentials file.")
                    return

                for ip_address in ip_addresses:
                    self.create_tab(ip_address)
                    self.update_data(ip_address)

        except FileNotFoundError:
            self.display_credentials_error()
            logging.error("Credentials file not found!")

    def display_no_ip_warning(self):
        # Displays a warning message when no IP addresses are found in the credentials file
        message_label = ctk.CTkLabel(self.tab_view, text="Please set the IP addresses of your devices in the credentials file")
        message_label.pack(pady=20)

    def display_credentials_error(self):
        # Displays an error message when the credentials file is not found
        error_label = ctk.CTkLabel(self.tab_view, text="Credentials file not found!")
        error_label.pack(pady=20)

    def create_tab(self, ip_address):
        # Creates a tab for a device with text areas, status labels, and buttons
        tab = self.tab_view.add(ip_address)
        main_frame = ctk.CTkFrame(tab)
        main_frame.pack(fill="both", expand=True)
        self.text_areas[ip_address] = ctk.CTkTextbox(main_frame)
        self.text_areas[ip_address].pack(fill="both", expand=True)
        status_label = ctk.CTkLabel(main_frame, text="STATUS")
        status_label.pack(pady=5)
        self.status_labels[ip_address] = status_label

        # Button to toggle switch
        toggle_button = ctk.CTkButton(tab, fg_color="transparent", border_width=2, text="Toggle", command=lambda addr=ip_address: self.toggle_switch(addr))
        toggle_button.pack(pady=5)
        
        # Button to open schedule setting window
        schedule_button = ctk.CTkButton(tab, fg_color="transparent", border_width=2, text="Set Schedule", command=lambda addr=ip_address: self.open_schedule_window(addr))
        schedule_button.pack(pady=5)

        # Button to chart power
        chart_button = ctk.CTkButton(tab, fg_color="transparent", border_width=2, text="Chart Power", command=lambda addr=ip_address: self.chart_power(addr))
        chart_button.pack(pady=5)

    def open_schedule_window(self, ip_address):
        # Opens the schedule setting window for a specific device
        schedule_window = ScheduleSettingWindow(ip_address)
        schedule_window.mainloop()

    def toggle_switch(self, ip_address):
        # Toggles the switch of a device and updates the status label accordingly
        try:
            url = f"http://{ip_address}/rpc/Switch.Toggle?id=0"
            response = requests.get(url)

            if '{"was_on":false}' in response.text:
                self.status_labels[ip_address].configure(text="OUTLET POWER IS ON")
            elif '{"was_on":true}' in response.text:
                self.status_labels[ip_address].configure(text="OUTLET POWER IS OFF")

        except requests.RequestException as e:
            self.handle_request_exception(ip_address, e)

    def chart_power(self, ip_address):
        # Charts the power consumption of a device over time
        try:
            url = f"http://{ip_address}/rpc/Switch.GetStatus?id=0"

            # Function to update the chart continuously
            def update_chart():
                try:
                    response = requests.get(url)
                    data = response.json()

                    apower = data.get("apower")

                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

                    timestamps.append(timestamp)
                    powers.append(apower)

                    if len(timestamps) > 12:
                        timestamps.pop(0)
                        powers.pop(0)

                    ax.clear()
                    ax.plot(timestamps, powers, marker='o', linestyle='-.')
                    ax.set_xlabel("Date and Time")
                    ax.set_ylabel("Power (WATTS)")
                    ax.set_title("Power Chart")
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    ax.spines['bottom'].set_visible(False)
                    ax.spines['left'].set_visible(False) 
                    ax.grid(False)
                    ax.figure.autofmt_xdate()
                    ax.set_facecolor('#333333')
                    ax.set_ylim(bottom=0)
                    ax.set_ylim(top=max(powers) + 250)

                    for i, power in enumerate(powers):
                        ax.text(timestamps[i], power, str(power), ha='center', va='bottom', color='white')

                    l = ax.fill_between(timestamps, powers)
                    l.set_facecolors([[.5,.5,.8,.3]])
                    l.set_edgecolors([[0,0,.5,.3]])
                    l.set_linewidths([3])

                    canvas.draw()

                    self.after(5000, update_chart)

                except requests.RequestException as e:
                    print(f"Error fetching data for {ip_address}: {e}")

            chart_button = self.tab_view.tab(ip_address).winfo_children()[-1]
            chart_button.pack_forget()

            chart_frame = ctk.CTkFrame(self.tab_view.tab(ip_address))
            chart_frame.pack()

            fig = Figure(figsize=(11, 4))
            ax = fig.add_subplot(211)
            fig.patch.set_facecolor('#212121')
            plt.style.use('dark_background')

            timestamps = []
            powers = []

            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.get_tk_widget().pack()

            fig.subplots_adjust(bottom=0.15)

            update_chart()

        except requests.RequestException as e:
            print(f"Error fetching data for {ip_address}: {e}")

    def update_data(self, ip_address):
        # Updates the data for a device including power, voltage, current, and temperature
        try:
            url = f"http://{ip_address}/rpc/Switch.GetStatus?id=0"
            response = requests.get(url)

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
        # Updates the UI with the latest data for a device
        temp_c = temperature.get('tC', 'N/A')
        temp_f = temperature.get('tF', 'N/A')

        self.text_areas[ip_address].delete("1.0", "end")
        self.text_areas[ip_address].insert("1.0", f"Watts: {apower}\nVolts: {voltage}\nAmps: {current}\nTemp (C): {temp_c}\nTemp (F): {temp_f}")

        if '"output":true' in response.text:
            self.status_labels[ip_address].configure(text="OUTLET POWER IS ON")
        elif '"output":false' in response.text:
            self.status_labels[ip_address].configure(text="OUTLET POWER IS OFF")

    def handle_request_exception(self, ip_address, e):
        # Handles exceptions that occur during requests and logs the errors
        error_msg = f"Error fetching data for {ip_address}: {e}"
        error_label = ctk.CTkLabel(self.tab_view, text=error_msg)
        error_label.pack(pady=20)
        logging.error(error_msg)

if __name__ == "__main__":
    app = MonitoringApp()
    app.mainloop()
