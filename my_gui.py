from datetime import datetime
import os
import subprocess
import customtkinter as ctk
from dotenv import dotenv_values
from tkdial import Meter
import requests
import psutil
from pymongo import MongoClient
from graph_utils import create_bar_graph, create_line_graph

ctk.set_appearance_mode("dark") 
ctk.set_default_color_theme("dark-blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Shelly Smart Plug US Monitoring Tool')
        self.resizable(0,0)
        self.eval('tk::PlaceWindow . center')
        self.ip_menu_frame = None
        self.monitoring_frame = None
        self.scheduling_menu = None
        self.history_menu = None
        self.main_frame = ctk.CTkFrame(self, fg_color="black", border_width=2, border_color="#1f538d")
        self.main_frame.grid(padx=1, pady=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.menu_control_frame = ctk.CTkFrame(self.main_frame, border_width=2, border_color="gray")
        self.menu_control_frame.grid(row=0, column=0, padx=5, pady=5)
        self.menu_control_frame.columnconfigure((0,1,2,3,4), weight=1)
        self.ip_menu_button = ctk.CTkButton(self.menu_control_frame, text='IP MENU', command=self.open_ip_menu)
        self.ip_menu_button.grid(row=0, column=0, padx=(10,5), pady=5)
        self.history_button = ctk.CTkButton(self.menu_control_frame, text='HISTORY MENU', command=self.open_history_menu)
        self.history_button.grid(row=0, column=2, padx=5, pady=5)
        self.scheduling_button = ctk.CTkButton(self.menu_control_frame, text='SCHEDULING MENU', command=self.open_scheduling_menu)
        self.scheduling_button.grid(row=0, column=4, padx=(5,10), pady=5)
        self.monitoring_button = ctk.CTkButton(self.menu_control_frame, text='MONITORING', command=self.open_monitoring)
        self.monitoring_button.grid(row=1, column=0, columnspan=5, sticky='nswe', padx=5, pady=5)
        self.db_button =ctk.CTkButton(self.menu_control_frame, text="START DB", command=self.start_db)
        self.db_button.grid(row=2, column=0, columnspan=5, sticky='nswe', padx=5, pady=5)

    def open_ip_menu(self):
        print('ip button pressed')
        if self.monitoring_frame:
            self.monitoring_frame.destroy()
            self.monitoring_frame = None
        if self.ip_menu_frame:
            self.ip_menu_frame.destroy()
            self.ip_menu_frame = None
        else:
            self.ip_menu_frame = IpMenu(self.main_frame)

    def open_history_menu(self):
        print('History button pressed')
        if self.monitoring_frame:
            if self.history_menu:
                self.history_menu.destroy() 
            self.history_menu = HistoryMenu(self, self.monitoring_frame)
        else:
            print("Monitoring window must be open to access history menu.")
            
    def open_scheduling_menu(self):
        if self.scheduling_menu:
            self.scheduling_menu.destroy()
        print('Scheduling button pressed')
        self.scheduling_menu = SchedulingMenu(self)

    def open_monitoring(self):
        print('monitoring button pressed')
        if self.ip_menu_frame:
            self.ip_menu_frame.destroy()
            self.ip_menu_frame = None
        if self.monitoring_frame:
            self.monitoring_frame.destroy()
            self.monitoring_frame = None
        else:
            self.monitoring_frame = Monitoring(self.main_frame)
    
    def start_db(self):
        script_name = 'test3.py'
        for process in psutil.process_iter():
            try:
                if script_name in process.cmdline():
                    print("Script is already running.")
                    self.db_button.configure(state="disabled", text="DB SCRIPT IS RUNNING", fg_color="transparent", text_color_disabled="white", border_width=2, border_color="#1f538d" )
                    return
            except psutil.AccessDenied:
                pass

        print("Starting script.")
        if os.name == 'posix': 
            subprocess.Popen(["python", script_name])
        elif os.name == 'nt':
            os.system(f"start python {script_name}")
        else:
            print("Unsupported operating system.")
            return
        self.db_button.configure(state="disabled", text="DB SCRIPT IS RUNNING", fg_color="transparent", text_color_disabled="white", border_width=2, border_color="#1f538d" )
        
class HistoryMenu(ctk.CTkToplevel):
    def __init__(self, master, monitoring_instance):
        super().__init__(master)
        self.monitoring_instance = monitoring_instance
        self.title("")
        self.resizable(0, 0)
        self.columnconfigure(0, weight=1)
        self.attributes('-topmost', True)
        self.create_widgets()
        self.populate_combobox()

    def create_widgets(self):
        self.main_frame = ctk.CTkFrame(self, border_width=2, border_color="gray")
        self.main_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        self.main_frame.columnconfigure(0, weight=1)

        self.title_frame = ctk.CTkFrame(self.main_frame)
        self.title_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        self.title_frame.columnconfigure(0, weight=1)

        self.title_label = ctk.CTkButton(
            self.title_frame,
            text="HISTORY MENU",
            state="disabled",
            fg_color="black",
            text_color_disabled="white",
            border_width=2,
            border_color="#1f538d"
        )
        self.title_label.grid(row=0, column=0, sticky="ew", padx=(10, 0), pady=10)

        self.combobox_frame = ctk.CTkFrame(self.main_frame)
        self.combobox_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.combobox_frame.columnconfigure(0, weight=1)

        self.combobox_label = ctk.CTkButton(
            self.combobox_frame,
            text="Select IP Address:",
            state="disabled",
            fg_color="transparent",
            text_color_disabled="white",
            border_width=2,
            border_color="gray"
        )
        self.combobox_label.grid(row=0, column=0, sticky="w", padx=(10, 5), pady=5)

        self.combobox_var = ctk.StringVar()
        self.combobox = ctk.CTkComboBox(self.combobox_frame, values=[], command=self.on_combobox_select, variable=self.combobox_var)
        self.combobox.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=5)
        self.combobox.bind("<<ComboboxSelected>>", self.on_combobox_select)

        self.db_entry_frame = ctk.CTkFrame(self, border_width=2)
        self.db_entry_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        self.db_entry_frame.columnconfigure((0,1), weight=1)
        
        self.db_date_entry = ctk.CTkEntry(self.db_entry_frame)
        self.db_date_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.db_date_button = ctk.CTkButton(self.db_entry_frame, text="Pull Data", command=self.search_db)
        self.db_date_button.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        self.history_cb_var = ctk.StringVar()
        self.history_cb = ctk.CTkComboBox(self.db_entry_frame, values=["Volts", "Amps", "Watts", "Total Energy (Wh)"], variable=self.history_cb_var)
        self.history_cb.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

    def populate_combobox(self):
        if os.path.exists('.env'):
            env_values = dotenv_values('.env')
            new_values = [value for key, value in env_values.items() if key.startswith('IP_ADDRESS_')]
            existing_values = list(self.combobox.cget("values"))
            all_values = existing_values + new_values
            self.combobox.configure(values=all_values)
            if all_values:
                self.combobox_var.set(all_values[0])

    def on_combobox_select(self, event):
        selected_ip = self.combobox_var.get()
        ip_address_sanitized = selected_ip.replace(".", "_")
        db_name = ip_address_sanitized
        client = MongoClient('172.31.74.135', 27017)
        db = client[db_name]
        collection_names = db.list_collection_names()

        if hasattr(self, 'text_box'):
            self.text_box.destroy()

        self.text_box = ctk.CTkTextbox(self, border_width=2, border_color="#1f538d")
        self.text_box.grid(row=1, column=0, padx=5, pady=5, sticky="nswe")
        self.text_box.configure(state="normal") 
        self.text_box.insert("end", "Available Dates:\n\n")

        for collection_name in collection_names:
            self.text_box.insert("end", collection_name + "\n")

        self.text_box.configure(state="disabled", height=180) 
        
    def search_db(self):
        client = MongoClient('172.31.74.135', 27017)

        try:
            selected_ip = self.combobox_var.get()
            db_name_sanitized = selected_ip.replace(".", "_")
            db = client[db_name_sanitized]
            coll_name = self.db_date_entry.get()
            collection = db[coll_name]
            measurement_mapping = {
                "Volts": "voltage",
                "Amps": "current",
                "Watts": "apower",
                "Total Energy (Wh)": "aenergy.total",
                "Timestamp": "timestamp"
            }
            measurement = self.history_cb_var.get()
            field_name = measurement_mapping.get(measurement)
            if field_name:
                print(f"All values of {field_name} in {coll_name}:")

                field_values = []
                timestamps = [] 
                prev_value = None  
                if measurement == "Total Energy (Wh)":
                    last_document = collection.find().sort([('timestamp', -1)]).limit(1)
                    for document in last_document:
                        if 'error_message' in document: 
                            continue
                        nested_keys = field_name.split('.')
                        value = document
                        for key in nested_keys:
                            value = value.get(key, {})
                        try:
                            field_values.append(float(value)) 
                            timestamps.append(document.get('timestamp')) 
                            prev_value = float(value)
                        except (ValueError, TypeError):
                            if prev_value is not None:
                                field_values.append(prev_value)
                                timestamps.append(document.get('timestamp'))
                            else:
                                field_values.append(0)
                                timestamps.append(document.get('timestamp'))
                else:
                    for document in collection.find():
                        if 'error_message' in document:
                            continue
                        nested_keys = field_name.split('.')
                        value = document
                        for key in nested_keys:
                            value = value.get(key, {})
                        try:
                            field_values.append(float(value))
                            timestamps.append(document.get('timestamp'))
                            prev_value = float(value)
                        except (ValueError, TypeError):
                            if prev_value is not None:
                                field_values.append(prev_value)  
                                timestamps.append(document.get('timestamp')) 
                            else:
                                field_values.append(0)
                                timestamps.append(document.get('timestamp'))  

                formatted_timestamps = [datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') for ts in
                                         timestamps]

                if measurement == "Total Energy (Wh)":
                    create_bar_graph(field_values, formatted_timestamps, "", "Total Energy (Wh)",
                                     f"Last Total Energy value on {coll_name} was {field_values[0]} Wh")
                elif measurement in ["Watts", "Volts", "Amps"]:
                    create_line_graph(field_values, formatted_timestamps, "", measurement,
                                      f"{measurement} values on {coll_name}")
                elif measurement == "Timestamp":
                    print("Timestamps:", formatted_timestamps)
                else:
                    print("Graph creation not implemented for this measurement yet.")

            else:
                print("Invalid measurement selected")
        except Exception as e:
            print("An error occurred:", e)
        finally:
            client.close()
        
class SchedulingMenu(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("")
        self.resizable(0,0)
        self.columnconfigure(0, weight=1)
        self.create_widgets()
        self.populate_combobox()
        self.view_schedule()
        self.attributes('-topmost', True)
        
    def create_widgets(self):
        self.main_frame = ctk.CTkFrame(self, border_width=2, border_color="gray")
        self.main_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        self.main_frame.columnconfigure(0, weight=1)

        self.title_frame = ctk.CTkFrame(self.main_frame)
        self.title_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        self.title_frame.columnconfigure(0, weight=1)
        self.title_label = ctk.CTkButton(self.title_frame, text="SCHEDULING MENU", state="disabled", fg_color="black", text_color_disabled="white", border_width=2, border_color="#1f538d")
        self.title_label.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.combobox_frame = ctk.CTkFrame(self.main_frame)
        self.combobox_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.combobox_frame.columnconfigure(0, weight=1)

        self.combobox_label = ctk.CTkButton(self.combobox_frame, text="Select IP Address:", state="disabled", fg_color="transparent", text_color_disabled="white", border_width=2, border_color="gray")
        self.combobox_label.grid(row=0, column=0, sticky="w", padx=(10, 5), pady=5)

        self.combobox_var = ctk.StringVar()
        self.combobox = ctk.CTkComboBox(self.combobox_frame, values=[], command=self.on_combobox_select, variable=self.combobox_var)
        self.combobox.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=5)
        self.combobox.bind("<<ComboboxSelected>>", self.on_combobox_select)

        self.textbox_frame = ctk.CTkFrame(self)
        self.textbox_frame.grid(row=2, column=0, sticky="nswe", padx=10, pady=5)
        self.textbox_frame.columnconfigure(0, weight=1)

        self.schedule_text = ctk.CTkTextbox(master=self.textbox_frame, corner_radius=6, height=85)
        self.schedule_text.grid(row=0, column=0, sticky="nswe")
        self.schedule_text.insert("0.0", "Active Schedules")

        self.button_frame = ctk.CTkFrame(self, border_width=2, border_color="#1f538d")
        self.button_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        self.button_frame.columnconfigure(0, weight=1)
        self.min_entry = ctk.CTkEntry(self.button_frame, placeholder_text="Minute")
        self.min_entry.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.hour_entry = ctk.CTkEntry(self.button_frame, placeholder_text="Hour")
        self.hour_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.day_entry = ctk.CTkEntry(self.button_frame, placeholder_text="Day")
        self.day_entry.grid(row=0, column=2, sticky="e", padx=5, pady=5)
        
        self.radio_var = ctk.IntVar(value=0)
        self.on_radio = ctk.CTkRadioButton(self.button_frame, text="Turn On", command=self.on_radiobutton_select, variable=self.radio_var, value=1)
        self.on_radio.grid(row=2, column=0, padx=5, pady=5)
        self.off_radio = ctk.CTkRadioButton(self.button_frame, text="Turn Off", command=self.on_radiobutton_select, variable=self.radio_var, value=2)
        self.off_radio.grid(row=2, column=1, padx=5, pady=5)
        self.toggle_radio = ctk.CTkRadioButton(self.button_frame, text="Toggle", command=self.on_radiobutton_select, variable=self.radio_var, value=3)
        self.toggle_radio.grid(row=2, column=2, padx=5, pady=5)
        
        self.add_schedule_button = ctk.CTkButton(self.button_frame, text="Create Schedule", command=self.add_schedule)
        self.add_schedule_button.grid(row=3, column=1, sticky="nswe", padx=5, pady=5)

        self.remove_entry = ctk.CTkEntry(self, placeholder_text="Enter Job ID #")
        self.remove_entry.grid(row=4, column=0, sticky="ew", padx=10, pady=5)
        self.remove_schedule_button = ctk.CTkButton(self, text="Remove Schedule", command=self.remove_schedule)
        self.remove_schedule_button.grid(row=5, column=0, sticky="ew", padx=10, pady=5)

    def populate_combobox(self):
        if os.path.exists('.env'):
            env_values = dotenv_values('.env')
            new_values = [value for key, value in env_values.items() if key.startswith('IP_ADDRESS_')]
            existing_values = list(self.combobox.cget("values"))
            all_values = existing_values + new_values
            self.combobox.configure(values=all_values)
            if all_values:
                self.combobox_var.set(all_values[0]) 
                
    def on_combobox_select(self, event):
        print("Combobox selection event triggered")
        self.view_schedule()

    def on_radiobutton_select(self):
        print("radiobutton toggled, current value:", self.radio_var.get())
    
    def add_schedule(self):
        try:
            selected_ip = self.combobox_var.get()
            day, minute, hour = self.day_entry.get(), int(self.min_entry.get()), int(self.hour_entry.get())
            if self.radio_var.get() == 1:
                params = '{"method":"switch.set","params":{"id":0,"on":true}}'
            elif self.radio_var.get() == 2:
                params = '{"method":"switch.set","params":{"id":0,"on":false}}'
            elif self.radio_var.get() == 3:
                params = '{"method":"switch.toggle","params":{"id":0}}'
            else:
                method_var = ""
            
            timespec = f"0 {minute} {hour} * * {day}"
            url = f"http://{selected_ip}/rpc/Schedule.Create?timespec={timespec}&calls=[{params}]"
            response = requests.get(url, timeout=10)
            data = response.json()
            if 'code' in data and data['code'] == -103:
                print(f"Failed to create schedule: {data.get('message', 'Unknown error')}")
            else:
                self.view_schedule()
                print("The schedule has been created successfully!")
        except ValueError:
            print("Failed to create a schedule: Please check your input values.")

    def view_schedule(self):
        self.schedule_text.configure(state="normal")
        print("Viewing existing schedules")
        self.schedule_text.delete("1.0", "end") 
        try:
            selected_ip = self.combobox_var.get()
            if not selected_ip:
                print("No IP address selected.")
                return

            response = requests.get(f"http://{selected_ip}/rpc/Schedule.List", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.schedule_text.insert("end", "List of saved schedules:\n")
                for job in data.get('jobs', []):
                    job_details = f"Job ID: {job.get('id', 'N/A')}, Enable: {job.get('enable', 'N/A')}, "
                    job_details += f"Timespec: {job.get('timespec', 'N/A')}, Method: {job.get('calls', [{}])[0].get('method', 'N/A')}\n"
                    self.schedule_text.insert("end", job_details)
                self.schedule_text.configure(state="disabled")
            else:
                print(f"Failed to fetch schedules. Status code: {response.status_code}")
                self.schedule_text.insert("end", "Failed to fetch schedules.\n")
                self.schedule_text.configure(state="disabled")
        except Exception as e:
            print(f"There was an issue fetching the list of schedules. Error: {e}")
            self.schedule_text.insert("end", f"There was an issue fetching the list of schedules. Error: {e}\n")
            self.schedule_text.configure(state="disabled")
            
    def remove_schedule(self):
        try:
            selected_ip = self.combobox_var.get()
            schedule_id = int(self.remove_entry.get())
            response = requests.get(f"http://{selected_ip}/rpc/Schedule.Delete?id={schedule_id}", timeout=10)
            data = response.json()
            if 'code' in data and data['code'] == -103:
                print(f"No schedule found with Job ID {schedule_id}")
            else:
                self.view_schedule()
                print(f"Schedule {schedule_id} deleted successfully!")
        except ValueError:
            print("Please enter a valid schedule ID number.")

class IpMenu(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid(row=2, column=0, padx=5, pady=5)        
        self.main_menu_frame = ctk.CTkFrame(self, border_width=2, border_color="gray")
        self.main_menu_frame.grid(row=0, column=0)
        self.db_ip_frame = ctk.CTkFrame(self.main_menu_frame)
        self.db_ip_frame.grid(row=0, column=1, sticky="new", padx=10, pady=(10,0))
        self.db_update_btn = ctk.CTkButton(self.db_ip_frame, text="Update")
        self.db_update_btn.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.db_update_ent = ctk.CTkEntry(self.db_ip_frame, placeholder_text="MONGO IP ADDRESS")
        self.db_update_ent.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        self.dev_update_frame = ctk.CTkFrame(self.main_menu_frame, border_width=2, border_color="#1f538d")
        self.dev_update_frame.grid(row=0, column=0, sticky="s", rowspan=2, padx=10, pady=10)
        self.ip_add_label = ctk.CTkButton(self.dev_update_frame, text='DEVICE IP', state="disabled", fg_color="transparent", text_color_disabled="white")
        self.ip_add_label.grid(row=0, column=0, padx=10, pady=10)
        self.ip_add_button = ctk.CTkButton(self.dev_update_frame, text='Add', command=self.add_ip)
        self.ip_add_button.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)        
        self.ip_list_cb = ctk.CTkEntry(self.dev_update_frame)
        self.ip_list_cb.grid(row=1, column=0, sticky="nswe", padx=10, pady=10)        
        self.ip_del_button = ctk.CTkButton(self.dev_update_frame, text='Delete', command=self.delete_ip)
        self.ip_del_button.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        self.ip_list_box = ctk.CTkTextbox(self.main_menu_frame,border_width=2, height=130, border_color="#1f538d")
        self.ip_list_box.grid(row=1, column=1, padx=10, pady=10, rowspan=2, sticky="ew")
        self.ip_addresses = set()
        self.read_env_file()
        self.view_ips()

    def add_ip(self):
        ip_address = self.ip_list_cb.get()
        if ip_address:
            if ip_address not in self.ip_addresses:
                self.ip_addresses.add(ip_address)
                self.update_env_file()
                print(f'Added IP address: {ip_address}')
                self.ip_list_cb.delete(0, 'end')
                self.view_ips()
            else:
                print(f'IP address {ip_address} already exists')
        else:
            print('Please enter a valid IP address')
        
    def delete_ip(self):
        ip_address = self.ip_list_cb.get()
        if ip_address in self.ip_addresses:
            self.ip_addresses.remove(ip_address)
            self.update_env_file()
            print(f'Deleted IP address: {ip_address}')    
            self.ip_list_cb.delete(0, 'end')
            self.view_ips()
        else:
            print(f'IP address {ip_address} not found')
            
    def update_env_file(self):
        with open('.env', 'w') as f:
            for i, ip_address in enumerate(self.ip_addresses, start=1):
                f.write(f'IP_ADDRESS_{i}={ip_address}\n')

    def read_env_file(self):
        if os.path.exists('.env'):
            env_values = dotenv_values('.env')
            for key, value in env_values.items():
                if key.startswith('IP_ADDRESS_'):
                    self.ip_addresses.add(value)
        else:
            print('No .env file found.')

    def view_ips(self):
        self.ip_list_box.configure(state="normal")
        self.ip_list_box.delete(1.0, 'end')        
        self.ip_list_box.insert('end', "Saved Device IP Addresses:\n\n")                
        if self.ip_addresses:
            for ip_address in self.ip_addresses:
                self.ip_list_box.insert('end', f'{ip_address}\n')
            self.ip_list_box.configure(state="disabled")
        else:
            self.ip_list_box.insert('end', 'No IP addresses found.')
            self.ip_list_box.configure(state="disabled")

class Monitoring(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="black")
        self.grid(row=2, column=0, columnspan=5, sticky="nswe", padx=5, pady=5)
        self.columnconfigure(1, weight=1)

        ip_addresses = []
        if os.path.exists('.env'):
            env_values = dotenv_values('.env')
            for key, value in env_values.items():
                if key.startswith('IP_ADDRESS_'):
                    ip_addresses.append(value)
        else:
            print('No .env file found.')

        self.tab_view = ctk.CTkTabview(self, border_width=2, fg_color="gray16", border_color="gray")
        self.tab_view.grid(row=0, column=0, columnspan=5, sticky="nswe", padx=5, pady=5)

        self.meter_frames = {}
        self.power_toggle_buttons = {}
        self.total_energy = {}
        self.temperature_f = {}
        self.temperature_labels = {}
        self.data_cache = {}

        self.update_meter_values()
        
        for ip_address in ip_addresses:
            tab = self.tab_view.add(ip_address)
            meters_frame = ctk.CTkFrame(tab, fg_color="gray16")
            meters_frame.grid(row=0, column=0, columnspan=3, sticky="nswe")

            power_toggle_button = ctk.CTkButton(meters_frame, hover="disabled", text="", font=("Roboto",30), height=100, border_width=2, border_color="#1f538d", command=self.toggle_power)
            power_toggle_button.grid(row=3, column=0, columnspan=3, sticky="nswe", padx=5, pady=5)

            self.power_toggle_buttons[ip_address] = power_toggle_button
            
            self.temp_frame = ctk.CTkFrame(meters_frame, fg_color="transparent")
            self.temp_frame.grid(row=1, column=1)
            temp_label = ctk.CTkButton(self.temp_frame, text="", hover="disabled", state="disabled", fg_color="transparent", text_color_disabled="white")
            temp_label.grid(row=0, column=0, sticky="we", padx=5, pady=5)

            self.temperature_labels[ip_address] = temp_label
            
            meters_label = ctk.CTkButton(meters_frame, fg_color="black", state="disabled", text_color_disabled="white", text="ACTIVE MONITORING", border_width=2, border_color="#1f538d")
            meters_label.grid(row=0, column=0, columnspan=3, sticky="nswe", padx=5, pady=5)

            watts_meter_frame = ctk.CTkFrame(meters_frame, fg_color="gray13", border_width=2, border_color="#1f538d")
            watts_meter_frame.grid(row=2, column=0, padx=10, pady=10)
            volts_meter_frame = ctk.CTkFrame(meters_frame, fg_color="gray13", border_width=2, border_color="#1f538d")
            volts_meter_frame.grid(row=2, column=1, padx=10, pady=10)
            amps_meter_frame = ctk.CTkFrame(meters_frame, fg_color="gray13", border_width=2, border_color="#1f538d")
            amps_meter_frame.grid(row=2, column=2, padx=10, pady=10)

            watts_meter = Meter(watts_meter_frame,
                                text="W (Power)",
                                text_font="Roboto 13",
                                fg="gray13",
                                radius=300,
                                start=0,
                                end=1800,
                                major_divisions=100,
                                minor_divisions=25,
                                border_width=0,
                                text_color="white",
                                start_angle=210,
                                end_angle=-240,
                                scale_color="white",
                                axis_color="white",
                                needle_color="#1f538d",
                                integer="True",
                                state="Unbind",
                                scroll=False)
            watts_meter.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)

            amps_meter = Meter(amps_meter_frame,
                               text="A (Current)",
                               text_font="Roboto 13",
                               fg="gray13",
                               radius=300,
                               start=0,
                               end=15,
                               major_divisions=1,
                               minor_divisions=0.25,
                               border_width=0,
                               text_color="white",
                               start_angle=210,
                               end_angle=-240,
                               scale_color="white",
                               axis_color="white",
                               needle_color="#1f538d",
                               state="Unbind",                               
                               scroll=False)
            amps_meter.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)

            volts_meter = Meter(volts_meter_frame,
                                text="V (Voltage)",
                                text_font="Roboto 13",
                                fg="gray13",
                                radius=300,
                                start=0,
                                end=140,
                                major_divisions=10,
                                minor_divisions=2.5,
                                border_width=0,
                                text_color="white",
                                start_angle=210,
                                end_angle=-240,
                                scale_color="white",
                                axis_color="white",
                                needle_color="#1f538d",
                                state="Unbind",
                                scroll="False")
            volts_meter.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)

            self.meter_frames[ip_address] = {
                'watts': watts_meter_frame,
                'volts': volts_meter_frame,
                'amps': amps_meter_frame
            }

    def update_meter_values(self):
        ip_address = self.tab_view.get()

        if not ip_address:
            self.after(1000, self.update_meter_values)
            return

        try:
            response = requests.get(f"http://{ip_address}/rpc/Switch.GetStatus?id=0")
            data = response.json()
            self.data_cache[ip_address] = {
                'watts': data.get("apower", 0),
                'amps': data.get("current", 0),
                'volts': data.get("voltage", 0),
                'output': data.get("output", 'true'),
                'total_energy': data.get("aenergy", {}).get("total", 0),
                'temperature_f': data.get("temperature", {}).get("tF", 0)
            }
            
            watts = data.get("apower", 0)
            amps = data.get("current", 0)
            volts = data.get("voltage", 0)
            output = data.get("output", 'true')
            total_energy = data.get("aenergy", {}).get("total", 0)
            temperature_f = data.get("temperature", {}).get("tF", 0)
            
            meters = self.meter_frames[ip_address]
            watts_meter = meters['watts'].grid_slaves(row=0, column=0)[0]
            amps_meter = meters['amps'].grid_slaves(row=0, column=0)[0]
            volts_meter = meters['volts'].grid_slaves(row=0, column=0)[0]

            watts_meter.set(watts)
            amps_meter.set(amps)
            volts_meter.set(volts)

            self.total_energy[ip_address] = total_energy
            
            temp_label = self.temperature_labels.get(ip_address)
            if temp_label:
                temp_label.configure(text=f'Temperature: {temperature_f}°F')
            
            power_toggle_button = self.power_toggle_buttons.get(ip_address)
            if power_toggle_button:
                if output:
                    power_toggle_button.configure(fg_color="green", text="POWER IS ON")
                else:
                    power_toggle_button.configure(fg_color="red", text="POWER IS OFF")

        except Exception as e:
            print(f"Error fetching data for {ip_address}: {e}")
            power_toggle_button = self.power_toggle_buttons.get(ip_address)
            if power_toggle_button:
                power_toggle_button.configure(fg_color="gray", text="DISCONNECTED")

        self.after(1000, self.update_meter_values)

    def get_cached_data(self, ip_address):
        return self.data_cache.get(ip_address, {})
        
    def toggle_power(self):
        active_tab = self.tab_view.get()
        ip_address = active_tab
        power_toggle_button = self.power_toggle_buttons.get(ip_address)

        try:
            response = requests.get(f"http://{ip_address}/rpc/Switch.Toggle?id=0")
            data = response.json()
            status = data.get('was_on')
            if status == "True":
                power_toggle_button.configure(fg_color="red", text="POWER IS OFF")
            elif status == "False":
                power_toggle_button.configure(fg_color="green", text="POWER IS ON")

        except Exception as e:
            print(f"Error fetching data for {ip_address}: {e}")


def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()