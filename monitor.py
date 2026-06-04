import io
import logging
import os
import threading
from collections import deque
from datetime import datetime

import customtkinter as ctk
import matplotlib.pyplot as plt
import numpy as np
import requests
from CTkMessagebox import CTkMessagebox
from dotenv import load_dotenv
from PIL import Image


logging.basicConfig(
    filename="monitoring.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class ScheduleWindow(ctk.CTkToplevel):
    def __init__(self, ip_address):
        super().__init__()
        self.ip_address = ip_address

        self.title(f"Schedules - {ip_address}")
        self.geometry("700x350")
        self.attributes("-topmost", True)

        self.main = ctk.CTkFrame(self)
        self.main.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(self.main, text="Create Toggle Schedule").grid(
            row=0, column=0, columnspan=3, pady=5
        )

        self.day_entry = ctk.CTkEntry(self.main, placeholder_text="Day 1-7")
        self.hour_entry = ctk.CTkEntry(self.main, placeholder_text="Hour 0-23")
        self.minute_entry = ctk.CTkEntry(self.main, placeholder_text="Minute 0-59")

        self.day_entry.grid(row=1, column=0, padx=5, pady=5)
        self.hour_entry.grid(row=1, column=1, padx=5, pady=5)
        self.minute_entry.grid(row=1, column=2, padx=5, pady=5)

        ctk.CTkButton(
            self.main,
            text="Create Toggle Schedule",
            command=self.create_schedule,
        ).grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        self.delete_entry = ctk.CTkEntry(self.main, placeholder_text="Schedule ID")
        self.delete_entry.grid(row=3, column=0, padx=5, pady=5)

        ctk.CTkButton(
            self.main,
            text="Delete Schedule",
            command=self.delete_schedule,
        ).grid(row=3, column=1, padx=5, pady=5)

        ctk.CTkButton(
            self.main,
            text="Refresh Schedule List",
            command=self.list_schedules,
        ).grid(row=3, column=2, padx=5, pady=5)

        self.schedule_text = ctk.CTkTextbox(self.main, height=150)
        self.schedule_text.grid(
            row=4,
            column=0,
            columnspan=3,
            padx=5,
            pady=10,
            sticky="nsew",
        )

        self.main.grid_columnconfigure((0, 1, 2), weight=1)
        self.main.grid_rowconfigure(4, weight=1)

        self.list_schedules()

    def shelly_get(self, path, params=None):
        response = requests.get(
            f"http://{self.ip_address}/rpc/{path}",
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def list_schedules(self):
        self.schedule_text.delete("1.0", "end")

        try:
            data = self.shelly_get("Schedule.List")
            jobs = data.get("jobs", [])

            if not jobs:
                self.schedule_text.insert("end", "No schedules found.\n")
                return

            for job in jobs:
                calls = job.get("calls", [])
                method = calls[0].get("method", "N/A") if calls else "N/A"

                self.schedule_text.insert(
                    "end",
                    f"ID: {job.get('id', 'N/A')} | "
                    f"Enabled: {job.get('enable', 'N/A')} | "
                    f"Time: {job.get('timespec', 'N/A')} | "
                    f"Method: {method}\n",
                )

        except Exception as e:
            CTkMessagebox(title="Error", message=f"Failed to list schedules:\n{e}")

    def create_schedule(self):
        try:
            day = int(self.day_entry.get())
            hour = int(self.hour_entry.get())
            minute = int(self.minute_entry.get())

            if not 1 <= day <= 7:
                raise ValueError("Day must be 1 through 7.")
            if not 0 <= hour <= 23:
                raise ValueError("Hour must be 0 through 23.")
            if not 0 <= minute <= 59:
                raise ValueError("Minute must be 0 through 59.")

            timespec = f"0 {minute} {hour} * * {day}"
            calls = '[{"method":"Switch.Toggle","params":{"id":0}}]'

            data = self.shelly_get(
                "Schedule.Create",
                {
                    "enable": "true",
                    "timespec": timespec,
                    "calls": calls,
                },
            )

            if "code" in data:
                raise RuntimeError(data.get("message", "Unknown schedule error"))

            CTkMessagebox(title="Success", message="Schedule created.")
            self.list_schedules()

        except Exception as e:
            CTkMessagebox(title="Error", message=f"Failed to create schedule:\n{e}")

    def delete_schedule(self):
        try:
            schedule_id = int(self.delete_entry.get())
            data = self.shelly_get("Schedule.Delete", {"id": schedule_id})

            if "code" in data:
                raise RuntimeError(data.get("message", "Unknown delete error"))

            CTkMessagebox(title="Success", message="Schedule deleted.")
            self.list_schedules()

        except Exception as e:
            CTkMessagebox(title="Error", message=f"Failed to delete schedule:\n{e}")


class MonitoringApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Shelly Plug Monitor")
        self.geometry("1200x800")
        self.minsize(1000, 700)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.status_labels = {}
        self.metric_labels = {}
        self.gauge_labels = {}
        self.chart_labels = {}
        self.last_seen_labels = {}
        self.history = {}

        self.main = ctk.CTkFrame(
            self,
            fg_color="#111111",
            border_width=1,
            border_color="#1f538d",
        )
        self.main.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_view = ctk.CTkTabview(
            self.main,
            fg_color="#050505",
            segmented_button_fg_color="#222222",
            segmented_button_selected_color="#1f538d",
            segmented_button_selected_hover_color="#2867aa",
            segmented_button_unselected_color="#111111",
            segmented_button_unselected_hover_color="#333333",
        )
        self.tab_view.pack(fill="both", expand=True, padx=8, pady=8)

        self.read_ips()

    def read_ips(self):
        load_dotenv(override=True)

        ip_addresses = []

        for i in range(1, 100):
            ip = os.getenv(f"IP_ADDRESS_{i}")
            if ip:
                ip_addresses.append(ip.strip())

        if not ip_addresses:
            CTkMessagebox(title="Error", message="No IP addresses found in .env")
            return

        for ip_address in ip_addresses:
            self.create_device_tab(ip_address)

    def create_device_tab(self, ip_address):
        tab = self.tab_view.add(ip_address)

        self.history[ip_address] = {
            "times": deque(maxlen=40),
            "watts": deque(maxlen=40),
            "amps": deque(maxlen=40),
            "volts": deque(maxlen=40),
        }

        frame = ctk.CTkFrame(tab, fg_color="#111111")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)
        frame.grid_rowconfigure(3, weight=2)

        self.status_labels[ip_address] = ctk.CTkButton(
            frame,
            text="Status: Unknown",
            command=lambda ip=ip_address: self.toggle_switch(ip),
            height=64,
            font=("Arial", 22, "bold"),
            border_width=1,
            border_color="#1f538d",
        )
        self.status_labels[ip_address].grid(
            row=0,
            column=0,
            columnspan=3,
            padx=6,
            pady=6,
            sticky="ew",
        )

        metrics_frame = ctk.CTkFrame(
            frame,
            fg_color="#181818",
            border_width=1,
            border_color="#333333",
        )
        metrics_frame.grid(
            row=1,
            column=0,
            columnspan=3,
            padx=6,
            pady=6,
            sticky="ew",
        )

        metrics = ["Watts", "Volts", "Amps", "WattHours", "Temp F"]
        self.metric_labels[ip_address] = {}

        for index, metric in enumerate(metrics):
            metrics_frame.grid_columnconfigure(index, weight=1)

            card = ctk.CTkFrame(
                metrics_frame,
                fg_color="#0b0b0b",
                border_width=1,
                border_color="#333333",
            )
            card.grid(row=0, column=index, padx=6, pady=6, sticky="ew")

            ctk.CTkLabel(
                card,
                text=metric,
                font=("Arial", 13, "bold"),
                text_color="#9cc8ff",
            ).pack(padx=8, pady=(8, 2))

            value_label = ctk.CTkLabel(
                card,
                text="0",
                font=("Arial", 24, "bold"),
                text_color="white",
            )
            value_label.pack(padx=8, pady=(2, 8))

            self.metric_labels[ip_address][metric] = value_label

        gauges_frame = ctk.CTkFrame(
            frame,
            fg_color="#181818",
            border_width=1,
            border_color="#333333",
        )
        gauges_frame.grid(
            row=2,
            column=0,
            columnspan=3,
            padx=6,
            pady=6,
            sticky="ew",
        )

        gauges_frame.grid_columnconfigure(0, weight=1)
        gauges_frame.grid_columnconfigure(1, weight=1)
        gauges_frame.grid_columnconfigure(2, weight=1)

        self.gauge_labels[ip_address] = {}

        for index, gauge_name in enumerate(["Power W", "Current A", "Voltage V"]):
            gauge_label = ctk.CTkLabel(
                gauges_frame,
                text=gauge_name,
                fg_color="#050505",
                corner_radius=8,
            )
            gauge_label.grid(row=0, column=index, padx=6, pady=6, sticky="nsew")
            self.gauge_labels[ip_address][gauge_name] = gauge_label

        chart_frame = ctk.CTkFrame(
            frame,
            fg_color="#181818",
            border_width=1,
            border_color="#333333",
        )
        chart_frame.grid(
            row=3,
            column=0,
            columnspan=3,
            padx=6,
            pady=6,
            sticky="nsew",
        )
        chart_frame.grid_columnconfigure(0, weight=1)
        chart_frame.grid_rowconfigure(0, weight=1)

        self.chart_labels[ip_address] = ctk.CTkLabel(
            chart_frame,
            text="Live history chart loading...",
            fg_color="#050505",
            corner_radius=8,
        )
        self.chart_labels[ip_address].grid(
            row=0,
            column=0,
            padx=6,
            pady=6,
            sticky="nsew",
        )

        buttons_frame = ctk.CTkFrame(
            frame,
            fg_color="#181818",
            border_width=1,
            border_color="#333333",
        )
        buttons_frame.grid(
            row=4,
            column=0,
            columnspan=3,
            padx=6,
            pady=6,
            sticky="ew",
        )

        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        buttons_frame.grid_columnconfigure(2, weight=1)

        ctk.CTkButton(
            buttons_frame,
            text="Set Schedule",
            command=lambda ip=ip_address: ScheduleWindow(ip),
        ).grid(row=0, column=0, padx=6, pady=8, sticky="ew")

        ctk.CTkButton(
            buttons_frame,
            text="Turn On",
            command=lambda ip=ip_address: self.set_switch(ip, True),
        ).grid(row=0, column=1, padx=6, pady=8, sticky="ew")

        ctk.CTkButton(
            buttons_frame,
            text="Turn Off",
            command=lambda ip=ip_address: self.set_switch(ip, False),
        ).grid(row=0, column=2, padx=6, pady=8, sticky="ew")

        self.last_seen_labels[ip_address] = ctk.CTkLabel(
            frame,
            text="Last update: never",
            text_color="#bbbbbb",
        )
        self.last_seen_labels[ip_address].grid(
            row=5,
            column=0,
            columnspan=3,
            padx=6,
            pady=(2, 6),
            sticky="w",
        )

        self.update_gauge_charts(ip_address, 0, 0, 0)
        self.update_history_chart(ip_address)
        self.update_device(ip_address)

    def shelly_get(self, ip_address, path, params=None):
        response = requests.get(
            f"http://{ip_address}/rpc/{path}",
            params=params,
            timeout=5,
        )
        response.raise_for_status()
        return response.json()

    def set_switch(self, ip_address, enabled):
        def worker():
            try:
                self.shelly_get(
                    ip_address,
                    "Switch.Set",
                    {
                        "id": 0,
                        "on": "true" if enabled else "false",
                    },
                )

                data = self.shelly_get(ip_address, "Switch.GetStatus", {"id": 0})
                self.after(0, lambda: self.apply_device_data(ip_address, data))

            except Exception as e:
                self.after(0, lambda: self.mark_disconnected(ip_address, e))

        threading.Thread(target=worker, daemon=True).start()

    def toggle_switch(self, ip_address):
        def worker():
            try:
                self.shelly_get(ip_address, "Switch.Toggle", {"id": 0})
                data = self.shelly_get(ip_address, "Switch.GetStatus", {"id": 0})
                self.after(0, lambda: self.apply_device_data(ip_address, data))

            except Exception as e:
                self.after(0, lambda: self.mark_disconnected(ip_address, e))

        threading.Thread(target=worker, daemon=True).start()

    def update_device(self, ip_address):
        def worker():
            try:
                data = self.shelly_get(ip_address, "Switch.GetStatus", {"id": 0})
                self.after(0, lambda: self.apply_device_data(ip_address, data))

            except Exception as e:
                self.after(0, lambda: self.mark_disconnected(ip_address, e))

            finally:
                self.after(3000, lambda: self.update_device(ip_address))

        threading.Thread(target=worker, daemon=True).start()

    def apply_device_data(self, ip_address, data):
        is_on = bool(data.get("output", False))

        self.status_labels[ip_address].configure(
            text="OUTLET POWER IS ON" if is_on else "OUTLET POWER IS OFF",
            fg_color="#008f39" if is_on else "#8f0000",
            hover_color="#00aa44" if is_on else "#aa0000",
        )

        watts = self.safe_float(data.get("apower", 0))
        volts = self.safe_float(data.get("voltage", 0))
        amps = self.safe_float(data.get("current", 0))
        watt_hours = self.safe_float(data.get("aenergy", {}).get("total", 0))
        temp_f = self.safe_float(data.get("temperature", {}).get("tF", 0))

        values = {
            "Watts": watts,
            "Volts": volts,
            "Amps": amps,
            "WattHours": watt_hours,
            "Temp F": temp_f,
        }

        for key, value in values.items():
            self.metric_labels[ip_address][key].configure(
                text=self.format_number(value)
            )

        now = datetime.now()

        self.history[ip_address]["times"].append(now.strftime("%H:%M:%S"))
        self.history[ip_address]["watts"].append(watts)
        self.history[ip_address]["amps"].append(amps)
        self.history[ip_address]["volts"].append(volts)

        self.update_gauge_charts(ip_address, watts, amps, volts)
        self.update_history_chart(ip_address)

        self.last_seen_labels[ip_address].configure(
            text=f"Last update: {now.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    def update_gauge_charts(self, ip_address, watts, amps, volts):
        self.render_gauge(
            label=self.gauge_labels[ip_address]["Power W"],
            value=watts,
            max_value=2000,
            title="Power",
            unit="W",
        )

        self.render_gauge(
            label=self.gauge_labels[ip_address]["Current A"],
            value=amps,
            max_value=20,
            title="Current",
            unit="A",
        )

        self.render_gauge(
            label=self.gauge_labels[ip_address]["Voltage V"],
            value=volts,
            max_value=250,
            title="Voltage",
            unit="V",
        )

    def render_gauge(self, label, value, max_value, title, unit):
        try:
            value = self.safe_float(value)
            percent = min(max(value / max_value, 0), 1)

            fig, ax = plt.subplots(figsize=(3.3, 2.1), dpi=100)
            fig.patch.set_facecolor("#050505")
            ax.set_facecolor("#050505")

            ax.set_xlim(-1.2, 1.2)
            ax.set_ylim(-0.25, 1.25)
            ax.axis("off")

            theta = np.linspace(180, 0, 120)
            x = np.cos(np.deg2rad(theta))
            y = np.sin(np.deg2rad(theta))

            ax.plot(x, y, linewidth=18, solid_capstyle="round", color="#333333")

            active_theta = np.linspace(180, 180 - (180 * percent), 120)
            active_x = np.cos(np.deg2rad(active_theta))
            active_y = np.sin(np.deg2rad(active_theta))

            ax.plot(
                active_x,
                active_y,
                linewidth=18,
                solid_capstyle="round",
                color="#1f77b4",
            )

            needle_angle = 180 - (180 * percent)
            needle_x = 0.88 * np.cos(np.deg2rad(needle_angle))
            needle_y = 0.88 * np.sin(np.deg2rad(needle_angle))

            ax.plot([0, needle_x], [0, needle_y], linewidth=3, color="white")
            ax.scatter([0], [0], s=45, color="white")

            ax.text(
                0,
                1.08,
                title,
                ha="center",
                va="center",
                color="white",
                fontsize=15,
                fontweight="bold",
            )

            ax.text(
                0,
                0.28,
                f"{self.format_number(value)} {unit}",
                ha="center",
                va="center",
                color="white",
                fontsize=19,
                fontweight="bold",
            )

            ax.text(-1.0, -0.05, "0", ha="center", color="#bbbbbb", fontsize=9)
            ax.text(
                1.0,
                -0.05,
                str(max_value),
                ha="center",
                color="#bbbbbb",
                fontsize=9,
            )

            image = self.fig_to_image(fig)
            plt.close(fig)

            ctk_image = ctk.CTkImage(
                dark_image=image,
                light_image=image,
                size=(330, 210),
            )

            label.configure(text="", image=ctk_image)
            label.image = ctk_image

        except Exception as e:
            logging.error("Failed to render gauge: %s", e)
            label.configure(
                text=f"{title}: {self.format_number(value)} {unit}",
                image=None,
            )

    def update_history_chart(self, ip_address):
        try:
            times = list(self.history[ip_address]["times"])
            watts = list(self.history[ip_address]["watts"])
            amps = list(self.history[ip_address]["amps"])
            volts = list(self.history[ip_address]["volts"])

            if not times:
                times = ["--"]
                watts = [0]
                amps = [0]
                volts = [0]

            x = list(range(len(times)))

            fig, axes = plt.subplots(
                3,
                1,
                figsize=(10.4, 3.2),
                dpi=100,
                sharex=True,
            )

            fig.patch.set_facecolor("#050505")

            chart_rows = [
                ("Watts", watts, axes[0]),
                ("Amps", amps, axes[1]),
                ("Volts", volts, axes[2]),
            ]

            for label, values, ax in chart_rows:
                ax.set_facecolor("#050505")
                ax.plot(x, values, marker="o", linewidth=2)
                ax.set_ylabel(label, color="white", fontsize=9)
                ax.tick_params(axis="y", colors="white", labelsize=8)
                ax.tick_params(axis="x", colors="white", labelsize=8)
                ax.grid(True, color="#222222", linewidth=0.8)

                for spine in ax.spines.values():
                    spine.set_color("#333333")

                max_value = max(values) if values else 0
                min_value = min(values) if values else 0

                if max_value == min_value:
                    padding = 1 if max_value == 0 else abs(max_value * 0.2)
                    ax.set_ylim(min_value - padding, max_value + padding)
                else:
                    padding = (max_value - min_value) * 0.2
                    ax.set_ylim(min_value - padding, max_value + padding)

            axes[0].set_title(
                "Live Monitoring History",
                color="white",
                fontsize=14,
                fontweight="bold",
                pad=6,
            )

            axes[2].set_xticks(x)

            if len(times) > 10:
                labels = []
                step = max(1, len(times) // 8)

                for index, item in enumerate(times):
                    labels.append(item if index % step == 0 else "")

                axes[2].set_xticklabels(labels, rotation=0)
            else:
                axes[2].set_xticklabels(times, rotation=0)

            fig.tight_layout(pad=1.0)

            image = self.fig_to_image(fig)
            plt.close(fig)

            ctk_image = ctk.CTkImage(
                dark_image=image,
                light_image=image,
                size=(1040, 320),
            )

            self.chart_labels[ip_address].configure(text="", image=ctk_image)
            self.chart_labels[ip_address].image = ctk_image

        except Exception as e:
            logging.error("Failed to render history chart: %s", e)
            self.chart_labels[ip_address].configure(
                text=f"History chart unavailable: {e}",
                image=None,
            )

    def fig_to_image(self, fig):
        buffer = io.BytesIO()
        fig.savefig(
            buffer,
            format="png",
            facecolor=fig.get_facecolor(),
            bbox_inches="tight",
            pad_inches=0.05,
        )
        buffer.seek(0)
        return Image.open(buffer)

    def mark_disconnected(self, ip_address, error):
        logging.error("Error fetching data for %s: %s", ip_address, error)

        self.status_labels[ip_address].configure(
            text="Disconnected",
            fg_color="#555555",
            hover_color="#666666",
        )

        for label in self.metric_labels[ip_address].values():
            label.configure(text="0")

        self.update_gauge_charts(ip_address, 0, 0, 0)

        self.last_seen_labels[ip_address].configure(text=f"Error: {error}")

    def safe_float(self, value):
        try:
            return float(value)
        except Exception:
            return 0.0

    def format_number(self, value):
        value = self.safe_float(value)

        if value == int(value):
            return str(int(value))

        return f"{value:.2f}"


if __name__ == "__main__":
    app = MonitoringApp()
    app.mainloop()
