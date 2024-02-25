"""
Module: shelly_monitor.py
Description: A simple GUI application for Shelly Monitoring Tool.
"""

import os
import customtkinter as ctk

def open_set_creds():
    """
    Function: open_set_creds
    Description: Opens the set credentials functionality.
    """
    os.system("python set_creds.py")

def open_monitoring():
    """
    Function: open_monitoring
    Description: Opens the monitoring functionality.
    """
    os.system("python monitor.py")

def main():
    """
    Function: main
    Description: Sets up the main application window and buttons.
    """
    root = ctk.CTk()
    root.title("Shelly Monitoring Tool")
    root.geometry("300x100")

    button_open_set_creds = ctk.CTkButton(root,
                                          fg_color="transparent",
                                          border_width=2,
                                          text="Set Credentials",
                                          command=open_set_creds)
    button_open_set_creds.pack(pady=10)

    button_print_credentials = ctk.CTkButton(root,
                                             fg_color="transparent",
                                             border_width=2,
                                             text="Begin Monitoring",
                                             command=open_monitoring)
    button_print_credentials.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
