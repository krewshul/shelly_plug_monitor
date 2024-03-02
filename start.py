import os
import requests
import logging
from dotenv import load_dotenv
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

def open_set_creds():
    """
    Function: open_set_creds
    Description: Opens the set credentials functionality.
    """
    os.system("python set_creds.py")

def open_monitoring():
    """
    Function: open_monitoring
    Description: Opens the monitoring functionality after verifying IP addresses.
    """
    if not check_env_file():
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
            response.raise_for_status()  # Raises an HTTPError if the response was an error response
        except requests.exceptions.RequestException as e:
            logging.error(f"Connection error for IP address {ip_address}: {e}")
            CTkMessagebox(title="Connection Error", message=f"Could not connect to {ip_address}. Please check the device and IP address.")
            return  # Stop execution and do not open the monitoring app if there is an error

    # If all IP addresses are reachable, open the monitoring app
    os.system("python monitor.py")

def check_env_file():
    """
    Function: check_env_file
    Description: Checks if the .env file exists.
    """
    return os.path.exists(".env")

def main():
    """
    Function: main
    Description: Sets up the main application window and buttons.
    """

    root = ctk.CTk()
    root.title("Shelly Monitoring Tool")
    root.geometry("300x100")
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    button_open_set_creds = ctk.CTkButton(root,
                                          fg_color="#1f538d",
                                          border_width=0,
                                          text="Set Credentials",
                                          command=open_set_creds)
    button_open_set_creds.pack(pady=10)

    button_print_credentials = ctk.CTkButton(root,
                                             fg_color="#1f538d",
                                             border_width=0,
                                             text="Begin Monitoring",
                                             command=open_monitoring)
    button_print_credentials.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    logging.basicConfig(filename='monitoring.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
    main()
