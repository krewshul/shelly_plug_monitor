import os
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

def open_set_creds():
    os.system("python set_creds.py")

def open_monitoring():
    os.system("python monitor.py")

def main():
    root = ctk.CTk()
    root.title("Shelly Monitoring Tool")
    root.geometry("300x100")
    button_open_set_creds = ctk.CTkButton(root, fg_color="transparent", border_width=2, text="Set Credentials", command=open_set_creds)
    button_open_set_creds.pack(pady=10)

    button_print_credentials = ctk.CTkButton(root, fg_color="transparent", border_width=2, text="Begin Monitoring", command=open_monitoring)
    button_print_credentials.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
