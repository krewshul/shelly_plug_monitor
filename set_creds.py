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

        # Main frame
        self.main_frame = ctk.CTkFrame(master, border_width=2, border_color="#1f538d")
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)

        # Frame for username and password
        self.credentials_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.credentials_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Username label and entry
        self.label_username = ctk.CTkLabel(self.credentials_frame, text="Username:")
        self.label_username.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.entry_username = ctk.CTkEntry(self.credentials_frame, width=200)
        self.entry_username.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Password label and entry
        self.label_password = ctk.CTkLabel(self.credentials_frame, text="Password:")
        self.label_password.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.entry_password = ctk.CTkEntry(self.credentials_frame, show="*", width=200)
        self.entry_password.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Adjusting for dynamic IP entry frames
        self.ip_entry_frames = []

        # Button to add IP address
        self.button_add_ip = ctk.CTkButton(self.main_frame,
                                           text="Add IP Address",
                                           corner_radius=8,
                                           command=self.add_ip_entry_frame)
        self.button_add_ip.grid(row=2, column=0, pady=10, padx=10, sticky="ew")

        # Update button
        self.button_update = ctk.CTkButton(self.main_frame,
                                           text="Update",
                                           corner_radius=8,
                                           command=self.update)
        self.button_update.grid(row=3, column=0, pady=10, padx=10, sticky="ew")

        # Make sure the credentials frame expands correctly
        self.credentials_frame.grid_columnconfigure(1, weight=1)

    def add_ip_entry_frame(self):
        """
        Method: add_ip_entry_frame
        Description: Adds entry fields for IP addresses dynamically.
        """
        ip_entry_frame = ctk.CTkFrame(self.main_frame)
        ip_entry_frame.grid(row=len(self.ip_entry_frames) + 3, column=0, sticky="ew", padx=10, pady=1)
        ip_entry = ctk.CTkEntry(ip_entry_frame, width=320)
        ip_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.ip_entry_frames.append(ip_entry_frame)

        # Ensure the main frame adjusts to new content
        self.main_frame.grid_rowconfigure(len(self.ip_entry_frames) + 2, weight=1)

        # Reposition the update button
        self.button_update.grid(row=len(self.ip_entry_frames) + 3, pady=10, padx=10, sticky="ew")

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

    def update(self):
        """
        Method: update
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
    ctk.set_appearance_mode("dark")  # Or "light" depending on your preference
    ctk.set_default_color_theme("blue")  # Choose a color theme
    root = ctk.CTk()
    LoginUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
