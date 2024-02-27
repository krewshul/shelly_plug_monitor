"""
Module: login_interface.py
Description: GUI for device login info
"""

import os
from dotenv import load_dotenv
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

class LoginUI:
    """
    Class: LoginUI
    Description: Represents the login interface.
    """

    def __init__(self, master):
        """
        Method: __init__
        Description: Initializes the LoginUI class.
        Parameters:
            - master: The master widget.
        """
        self.master = master
        self.master.title("Set Credentials")

        self.label_username = ctk.CTkLabel(master, text="Username:")
        self.label_username.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.entry_username = ctk.CTkEntry(master)
        self.entry_username.grid(row=0, column=1, padx=10, pady=5)

        self.label_password = ctk.CTkLabel(master, text="Password:")
        self.label_password.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.entry_password = ctk.CTkEntry(master, show="*")
        self.entry_password.grid(row=1, column=1, padx=10, pady=5)

        self.ip_entry_frames = []

        self.button_add_ip = ctk.CTkButton(master,
                                           fg_color="transparent",
                                           border_width=2,
                                           text="Add IP Address",
                                           command=self.add_ip_entry_frame)
        self.button_add_ip.grid(row=2, column=1, pady=10, padx=5, sticky="news")

        self.button_login = ctk.CTkButton(master,
                                          fg_color="transparent",
                                          border_width=2,
                                          text="Update",
                                          command=self.login)
        self.button_login.grid(row=3, column=1, pady=10, padx=5, sticky="news")

    def add_ip_entry_frame(self):
        """
        Method: add_ip_entry_frame
        Description: Adds entry fields for IP addresses dynamically.
        """
        ip_entry_frame = ctk.CTkFrame(self.master)
        ip_entry_frame.grid(sticky="ew", padx=10, pady=5)
        ip_entry = ctk.CTkEntry(ip_entry_frame)
        ip_entry.grid(row=0, column=0, padx=5)
        self.ip_entry_frames.append(ip_entry_frame)

        self.button_login.grid_forget()  # Temporarily forget the "Login" button
        for i, frame in enumerate(self.ip_entry_frames, start=3):
            frame.grid(row=i, column=1, pady=5, sticky="ew")
        self.button_login.grid(row=len(self.ip_entry_frames) + 3,
                               column=1, pady=10,
                               sticky="se")  # Re-add the "Login" button

    def get_ip_addresses(self):
        """
        Method: get_ip_addresses
        Description: Retrieves the IP addresses entered by the user.
        Returns:
            - ip_addresses: A list of IP addresses.
        """
        ip_addresses = []
        for frame in self.ip_entry_frames:
            ip_entry = frame.grid_slaves(row=0, column=0)[0]
            ip_addresses.append(ip_entry.get())
        return ip_addresses

    def login(self):
        """
        Method: login
        Description: Writes login variables to ".env" file.
        """
        username = self.entry_username.get()
        password = self.entry_password.get()
        ip_addresses = self.get_ip_addresses()

        try:
            # Create or load existing .env file
            load_dotenv()
            
            with open(".env", "w", encoding="utf-8") as file:
                # Write username and password
                file.write(f'USERNAME={username}\n')
                file.write(f'PASSWORD={password}\n')

                # Write IP addresses
                for i, ip in enumerate(ip_addresses, start=1):
                    file.write(f'IP_ADDRESS_{i}={ip}\n')

            CTkMessagebox(master=self.master,
                          title="Success!",
                          message="Credentials have been updated!",
                          icon="check")
        except Exception as e:
            CTkMessagebox(title="Error!",
                          message=f"Failed to update .env file: {e}",
                          icon="error")

def main():
    """
    Function: main
    Description: Sets up the Tkinter application window.
    """
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    root = ctk.CTk()
    LoginUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
