import os
import requests
import logging
from dotenv import load_dotenv
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

class MonitoringToolApp:
    def __init__(self, root):
        """
        Initialize the MonitoringToolApp class.
        """
        self.root = root
        self.setup_UI()

    def setup_UI(self):
        """
        Sets up the user interface.
        """
        self.root.title(" ")
        ctk.set_appearance_mode("dark")  # Set theme
        ctk.set_default_color_theme("dark-blue")

        # Create a main frame to hold other widgets
        self.main_frame = ctk.CTkFrame(self.root, border_width=1, border_color="#1f538d")
        self.main_frame.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")

        # Set Credentials Button
        self.button_open_set_creds = ctk.CTkButton(self.main_frame,
                                                   fg_color="#1f538d",
                                                   border_width=0,
                                                   text="Set Credentials",
                                                   command=self.open_set_creds)
        self.button_open_set_creds.grid(row=0, column=0, padx=5, pady=5)

        # Begin Monitoring Button
        self.button_begin_monitoring = ctk.CTkButton(self.main_frame,
                                                     fg_color="#1f538d",
                                                     border_width=0,
                                                     text="Begin Monitoring",
                                                     command=self.open_monitoring)
        self.button_begin_monitoring.grid(row=1, column=0, padx=5, pady=5)

    def open_set_creds(self):
        """
        Opens the set credentials functionality.
        """
        os.system("python set_creds.py")

    def open_monitoring(self):
        """
        Opens the monitoring functionality after verifying IP addresses.
        """
        if not self.check_env_file():
            CTkMessagebox(title="Error", message="No .env file found. Please set your credentials.")
            return

        # Load the environment variables
        load_dotenv(override=True)
        ip_addresses = [os.getenv(f'IP_ADDRESS_{i}') for i in range(1, 100) if os.getenv(f'IP_ADDRESS_{i}')]

        if not ip_addresses:
            CTkMessagebox(title="Error", message="No IP addresses found in .env file. Please set your credentials.")
            return

        # Check connectivity to each IP address
        for ip_address in ip_addresses:
            try:
                response = requests.get(f"http://{ip_address}/rpc/Switch.GetStatus?id=0", timeout=5)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                logging.error(f"Connection error for IP address {ip_address}: {e}")
                CTkMessagebox(title="Connection Error", message=f"Could not connect to {ip_address}. Please check the device and IP address.")
                return

        # If all IP addresses are reachable, open the monitoring app
        os.system("python monitor.py")

    def check_env_file(self):
        """
        Checks if the .env file exists.
        """
        return os.path.exists(".env")


def main():
    logging.basicConfig(filename='monitoring.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
    root = ctk.CTk()
    app = MonitoringToolApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
