import customtkinter as ctk
import requests
import logging
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import time


class MonitoringApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_logging()
        self.read_credentials()

    def setup_ui(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.title("Devices")
        self.geometry("850x600")

        # Create scrollable frame to contain tab view
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)

        # Create tab view inside scrollable frame
        self.tab_view = ctk.CTkTabview(self.main_frame)
        self.tab_view.pack(fill="both", expand=True)

        # Dictionary to store text areas for each IP address
        self.text_areas = {}
        # Dictionary to store status labels for each IP address
        self.status_labels = {}

    def setup_logging(self):
        logging.basicConfig(filename='monitoring.log', level=logging.ERROR,
                            format='%(asctime)s - %(levelname)s - %(message)s')

    def read_credentials(self):
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

                # Create tab for each IP address
                for ip_address in ip_addresses:
                    self.create_tab(ip_address)
                    self.update_data(ip_address)

        except FileNotFoundError:
            self.display_credentials_error()
            logging.error("Credentials file not found!")

    def display_no_ip_warning(self):
        message_label = ctk.CTkLabel(self.tab_view, text="Please set the IP addresses of your devices in the credentials file")
        message_label.grid(row=0, column=0, pady=20, sticky="nsew")

    def display_credentials_error(self):
        error_label = ctk.CTkLabel(self.tab_view, text="Credentials file not found!")
        error_label.grid(row=0, column=0, pady=20, sticky="nsew")

    def create_tab(self, ip_address):
        tab = self.tab_view.add(ip_address)

        # Create scrollable frame within tab
        main_frame = ctk.CTkFrame(tab)
        main_frame.pack(fill="both", expand=True)

        # Create scrollable area within tab
        self.text_areas[ip_address] = ctk.CTkTextbox(main_frame)
        self.text_areas[ip_address].pack(fill="both", expand=True)

        # Create label above the button with name "STATUS"
        status_label = ctk.CTkLabel(main_frame, text="STATUS")
        status_label.pack(pady=5)
        self.status_labels[ip_address] = status_label

        # Create button within tab
        button = ctk.CTkButton(tab, fg_color="transparent", border_width=2, text="Toggle", command=lambda addr=ip_address: self.toggle_switch(addr))
        button.pack(pady=10)

        # Create button to chart power
        chart_button = ctk.CTkButton(tab, fg_color="transparent", border_width=2, text="Chart Power", command=lambda addr=ip_address: self.chart_power(addr))
        chart_button.pack(pady=5)

    def update_data(self, ip_address):
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
        self.text_areas[ip_address].delete("1.0", "end")
        self.text_areas[ip_address].insert("1.0", f"Power: {apower}\nVoltage: {voltage}\nCurrent: {current}\nTemperature: {temperature}")

        if '"output":true' in response.text:
            self.status_labels[ip_address].configure(text="OUTLET POWER IS ON")
        elif '"output":false' in response.text:
            self.status_labels[ip_address].configure(text="OUTLET POWER IS OFF")

    def handle_request_exception(self, ip_address, e):
        error_msg = f"Error fetching data for {ip_address}: {e}"
        error_label = ctk.CTkLabel(self.tab_view, text=error_msg)
        error_label.pack(pady=20)
        logging.error(error_msg)

    def toggle_switch(self, ip_address):
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
        try:
            url = f"http://{ip_address}/rpc/Switch.GetStatus?id=0"

            def update_chart():
                try:
                    response = requests.get(url)
                    data = response.json()

                    # Extract apower value
                    apower = data.get("apower")

                    # Generate current timestamp
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

                    # Append the new data to lists
                    timestamps.append(timestamp)
                    powers.append(apower)

                    # Keep only the last 12 data points
                    if len(timestamps) > 12:
                        timestamps.pop(0)
                        powers.pop(0)
                    plt.rcParams.update({'font.size': 9})

                    # Update the plot data
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
                    ax.figure.autofmt_xdate()  # Automatically format the x-axis dates
                    # Set the background color of the chart
                    ax.set_facecolor('#333333')

                    # Set padding of chart
                    ax.set_ylim(bottom=0)  # Ensure bottom limit is 0
                    ax.set_ylim(top=max(powers) + 250)  # Add padding at the top

                    # Annotate each data point on the y-axis
                    for i, power in enumerate(powers):
                        ax.text(timestamps[i], power, str(power), ha='center', va='bottom', color='white')

                    l = ax.fill_between(timestamps, powers)
                    l.set_facecolors([[.5,.5,.8,.3]])
                    l.set_edgecolors([[0,0,.5,.3]])
                    l.set_linewidths([3])

                    # Redraw the canvas
                    canvas.draw()

                    # Schedule the next update after 5 second
                    self.after(5000, update_chart)

                except requests.RequestException as e:
                    print(f"Error fetching data for {ip_address}: {e}")

            # Remove the button widget
            chart_button = self.tab_view.tab(ip_address).winfo_children()[-1]
            chart_button.destroy()

            # Create a frame within the tab view for the chart
            chart_frame = ctk.CTkFrame(self.tab_view.tab(ip_address))
            chart_frame.pack(side='top', fill='both', expand=True)

            # Create a figure and subplot
            fig = Figure(figsize=(11, 4))
            ax = fig.add_subplot(211)
            fig.patch.set_facecolor('#212121')
            plt.style.use('dark_background')
            # Create empty lists to store data
            timestamps = []
            powers = []

            # Embed the plot into the tkinter window
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.get_tk_widget().pack(side='top', fill="x", expand=True)

            # Adjust subplot parameters to add padding to the bottom
            fig.subplots_adjust(bottom=0.15)

            # Schedule initial update
            update_chart()

        except requests.RequestException as e:
            print(f"Error fetching data for {ip_address}: {e}")


if __name__ == "__main__":
    app = MonitoringApp()
    app.mainloop()
