import os
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
    Description: Opens the monitoring functionality.
    """
    if not check_env_file():
        CTkMessagebox(title="Error!",
                      message="No .env file found. Please set your credentials.",
                      icon="cancel")
    else:
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
