import os
import subprocess
import sys

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from dotenv import load_dotenv


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.ip_entries = []

        self.root.title("Shelly Plug Monitor")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.main_frame = ctk.CTkFrame(
            root,
            border_width=1,
            border_color="#1f538d",
        )
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.add_button = ctk.CTkButton(
            self.main_frame,
            text="Add IP Address",
            command=self.add_ip_entry,
        )
        self.add_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.update_button = ctk.CTkButton(
            self.main_frame,
            text="Update",
            command=self.update_env,
        )

        self.start_button = ctk.CTkButton(
            self.main_frame,
            text="Begin Monitoring",
            command=self.open_monitoring,
        )

        self.load_existing_ips()
        self.reflow_buttons()

    def load_existing_ips(self):
        load_dotenv(override=True)

        found_any = False

        for i in range(1, 100):
            ip = os.getenv(f"IP_ADDRESS_{i}")
            if ip:
                self.add_ip_entry(ip)
                found_any = True

        if not found_any:
            self.add_ip_entry()

    def add_ip_entry(self, value=""):
        row = len(self.ip_entries) + 1

        entry = ctk.CTkEntry(
            self.main_frame,
            placeholder_text="192.168.0.140",
            width=250,
        )
        entry.insert(0, value)
        entry.grid(row=row, column=0, padx=10, pady=5, sticky="ew")

        self.ip_entries.append(entry)
        self.reflow_buttons()

    def reflow_buttons(self):
        button_row = len(self.ip_entries) + 1

        self.update_button.grid(
            row=button_row,
            column=0,
            padx=10,
            pady=(10, 5),
            sticky="ew",
        )

        self.start_button.grid(
            row=button_row + 1,
            column=0,
            padx=10,
            pady=(5, 10),
            sticky="ew",
        )

    def get_ip_addresses(self):
        ips = []

        for entry in self.ip_entries:
            ip = entry.get().strip()
            if ip:
                ips.append(ip)

        return ips

    def update_env(self):
        ips = self.get_ip_addresses()

        if not ips:
            CTkMessagebox(
                title="Error",
                message="Please add at least one IP address.",
            )
            return

        try:
            with open(".env", "w", encoding="utf-8") as file:
                for i, ip in enumerate(ips, start=1):
                    file.write(f"IP_ADDRESS_{i}={ip}\n")

            CTkMessagebox(
                title="Success",
                message="IP addresses saved.",
            )

        except Exception as e:
            CTkMessagebox(
                title="Error",
                message=f"Failed to save .env file:\n{e}",
            )

    def open_monitoring(self):
        if not os.path.exists(".env"):
            CTkMessagebox(
                title="Error",
                message="No .env file found. Press Update first.",
            )
            return

        subprocess.Popen([sys.executable, "monitor.py"])


def main():
    root = ctk.CTk()
    app = LoginApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
