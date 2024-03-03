import os
import requests
import logging
from dotenv import load_dotenv
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

class LoginApp:
    def __init__(self, root):
        # Initialize the LoginApp class
        self.root = root
        self.ip_entry_frames = []  # List to hold dynamically created IP entry frames
        self.setup_UI()  # Set up the user interface

    def setup_UI(self):
        # Set up the user interface
        self.root.title("Set Credentials for Monitoring")  # Set window title
        ctk.set_appearance_mode("dark")  # Set theme to dark mode
        ctk.set_default_color_theme("blue")  # Set default color theme

        # Main frame to hold all UI elements
        self.main_frame = ctk.CTkFrame(self.root, border_width=1, border_color="#1f538d")
        self.main_frame.grid(row=0, column=0, padx=2, pady=2, sticky="ns")

        # Button to add IP address entry
        self.button_add_ip = ctk.CTkButton(self.main_frame,
                                           text="Add IP Address",
                                           fg_color="#1f538d",
                                           border_width=0,
                                           command=self.add_ip_entry_frame)
        self.button_add_ip.grid(row=1, column=0, pady=10, padx=10, sticky="ew")

        # Button to update credentials
        self.button_update = ctk.CTkButton(self.main_frame,
                                           text="Update",
                                           fg_color="#1f538d",
                                           border_width=0,
                                           command=self.update)
        self.button_update.grid(row=2, column=0, pady=10, padx=10, sticky="ew")

        # Button to begin monitoring
        self.button_begin_monitoring = ctk.CTkButton(self.main_frame,
                                                     fg_color="#1f538d",
                                                     border_width=0,
                                                     text="Begin Monitoring",
                                                     command=self.open_monitoring)
        self.button_begin_monitoring.grid(row=3, column=0, padx=5, pady=5)

    def add_ip_entry_frame(self):
        # Function to add entry fields for IP addresses dynamically
        ip_entry_frame = ctk.CTkFrame(self.main_frame)
        ip_entry_frame.grid(row=len(self.ip_entry_frames) + 2, column=0, sticky="ew", padx=10, pady=1)
        ip_entry = ctk.CTkEntry(ip_entry_frame)
        ip_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.ip_entry_frames.append(ip_entry_frame)

        # Ensure main frame adjusts to new content
        self.main_frame.grid_rowconfigure(len(self.ip_entry_frames) + 1, weight=1)

        # Reposition update and begin monitoring buttons
        self.button_update.grid(row=len(self.ip_entry_frames) + 2, pady=10, padx=10, sticky="ew")
        self.button_begin_monitoring.grid(row=len(self.ip_entry_frames) + 3, padx=5, pady=5)

    def update(self):
        # Function to write IP addresses to ".env" file
        ip_addresses = self.get_ip_addresses()

        try:
            # Create or load existing .env file
            load_dotenv()
            
            with open(".env", "w", encoding="utf-8") as file:
                # Write IP addresses
                for i, ip in enumerate(ip_addresses, start=1):
                    file.write(f'IP_ADDRESS_{i}={ip}\n')

            # Display success message
            CTkMessagebox(master=self.root,
                          title="Success!",
                          message="IP addresses have been updated!",
                          icon="check")
        except Exception as e:
            # Display error message if updating fails
            CTkMessagebox(title="Error!",
                          message=f"Failed to update .env file: {e}",
                          icon="cancel")

    def get_ip_addresses(self):
        # Function to retrieve the IP addresses entered by the user
        ip_addresses = []
        for frame in self.ip_entry_frames:
            ip_entry = frame.grid_slaves(row=0, column=0)[0]
            ip_addresses.append(ip_entry.get())
        return ip_addresses

    def open_monitoring(self):
        # Function to open the monitoring functionality after verifying IP addresses
        if not self.check_env_file():
            # Check if .env file exists
            CTkMessagebox(title="Error", message="No .env file found. Please set IP addresses.")
            return

        # Load environment variables
        load_dotenv(override=True)

        # Retrieve IP addresses from .env
        ip_addresses = [os.getenv(f'IP_ADDRESS_{i}') for i in range(1, 100) if os.getenv(f'IP_ADDRESS_{i}')]

        if not ip_addresses:
            # Check if IP addresses are set in .env
            CTkMessagebox(title="Error", message="No IP addresses found in .env file. Please add at least one IP address.")
            return

        # Open the monitoring app if IP addresses are set
        os.system("python monitor.py")

    def check_env_file(self):
        # Function to check if the .env file exists
        return os.path.exists(".env")

def main():
    # Main function to initialize the application
    logging.basicConfig(filename='login_app.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
    root = ctk.CTk()  # Create tkinter root window
    app = LoginApp(root)  # Initialize LoginApp instance
    root.mainloop()  # Start tkinter event loop

if __name__ == "__main__":
    main()
