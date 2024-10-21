import subprocess
import os
import platform
import time
import json
import threading
import socket

from tkinter import *
import tkinter as tk

from api_consts import GET_DATA_URL, UPDATE_QUEUE_URL, PRINTERS_LIST_URL
from api_client import ApiClient
from print_request import PrintRequest
from printer import Printer


## Global variables
base_url = None
is_running = False
auth_token = None


def get_printers_list():
    url = f"{base_url}{PRINTERS_LIST_URL}{auth_token}"
    api_client = ApiClient(url=url, method="GET")

    response = api_client.execute()

    if response["success"]:
        printers = response["data"]["items"]

        for p in printers:
            printers_list.insert(tk.END, p["printer_name_at_location"])


## Save server base url and auth token in local memory
## then starts the service
def set_api_url():
    global base_url
    global auth_token

    base_url = urlField.get()
    auth_token = tokenField.get() 

    get_printers_list()
    
    ## Run the service in a different thread to not block GUI functionalities
    thread = threading.Thread(target=start, daemon=True)
    thread.start()


## Start the service
def start():
    global is_running
    is_running = True
    status.config(fg="green", text="Active")
    orders_url = f"{base_url}{GET_DATA_URL}{auth_token}"

    ## Run until "stop" is pressed
    while is_running:
        api_client = ApiClient(url=orders_url, method="GET")
        response = api_client.execute()

        if response["success"]:
            data = response["data"]
            orders = data["items"]
            
            for o in orders:
                order = PrintRequest().from_json(o)
                seq_no = order.seq_no
                printer_name = order.printer_name

                printer_ip = find_printer(printer_name)
                
                ## Printer found
                if printer_ip is not None:
                    template_content = order.data

                    if template_content is not None:
                        printer = Printer(ip=printer_ip, content=template_content)
                        
                        is_printed = printer.print()

                        if is_printed:
                            ## update printing sequence
                            update_queue(seq_no)

                        else:
                            ## show error
                            print("AAAAAA")

                ## Printer was not found
                else:
                    pass
                    # Send error message
                    

                ## Wait n of seconds between printing
                time.sleep(3)

                if not is_running:
                    break

        else:
            print(response)
        ## Wait n of seconds before fetching new orders
        time.sleep(5)


## Stop the service
def stop():
    global is_running
    is_running = False
    status.config(fg="red", text="Inactive")
    print("The service is stopped")


def os_name() -> str:
    return platform.system()



## Returns the selected printer IP Address
def find_printer(printer_name: str) -> str:
    if os_name() == "Windows":
        return get_printer_ip_windows(printer_name)
    
    elif os_name == "Linux":
        return get_printer_ip_linux(printer_name)


def open_cash_drawer(printer_socket):
    # ESC d p t command to open cash drawer (first drawer)
    command = bytes([0x1B, 0x64, 0x00, 0x1E])
    printer_socket.sendall(command)
    

def update_queue(seq_no: int):
    url = f"{base_url}{UPDATE_QUEUE_URL}{seq_no}"
    api_client = ApiClient(url=url, method="PUT")

    response = api_client.execute()

    if response["success"]:
        pass


## Returns printer ip by name.
## If the printer was not found, returns None.
## Windows Only
def get_printer_ip_windows(printer_name: str) -> str:
    import win32print
    printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
   
    for printer in printers:
        print(f"Printer Name: {printer[2]}")
        if printer[2] == printer_name:
            # Open the printer and get its attributes
            handle = win32print.OpenPrinter(printer[2])
            printer_info = win32print.GetPrinter(handle, 2)
            
            # Extract port name (where the printer is connected)
            port_name = printer_info['pPortName']
            print(f"Port Name: {port_name}\n")
            
            win32print.ClosePrinter(handle)

            return str(port_name)
        
    print(f"Printer ({printer_name}) was not found")
    return None


## Returns printer ip by name.
## If the printer was not found, returns None.
## Linux Only
def get_printer_ip_linux(printer_name: str) -> str:
    try:
        printer_name = printer_name.replace(" ", "_")
        # Get list of devices
        output = subprocess.check_output(["lpstat", "-p", "-d"]).decode("utf-8")
        printers = output.splitlines()
        
        for printer in printers:
            ## Check if device is a printer
            if "printer" in printer:
                printer_info = printer.split()
                p_name = printer_info[1]
                
                # Get device URI to extract IP address
                if p_name == printer_name:
                    uri_output = subprocess.check_output(["lpstat", "-v"]).decode("utf-8")
                    for line in uri_output.splitlines():
                        if p_name in line:
                            uri = line.split("://")[1]
                            ip_address = uri.split("/")[0]
                            return ip_address
        return None

    except subprocess.CalledProcessError as e:
        return None


################################################################
######################### Building GUI #########################
################################################################

def center_window(window, width=300, height=200):
    # Get the screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Calculate the position for the window to be centered
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    
    # Set the window's geometry to the calculated position
    window.geometry(f'{width}x{height}+{x}+{y}')


root = Tk()

# root window title and dimension
root.title("Printing Hub")

center_window(root, 400, 300)

# Configure the root window's grid to make column 0 expandable
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

main_frame = tk.Frame(root)
main_frame.grid(row=0, column=0, sticky="new")

list_frame = tk.Frame(root)
list_frame.grid(row=2, column=0, sticky="sew")

# Make sure list_frame takes all available space
list_frame.grid_columnconfigure(0, weight=1)

### First row ###
urlLabel = tk.Label(
    main_frame, 
    text="URL: "
) 
urlLabel.grid(row=0, column=0)

# URL Textbox
urlField = tk.Entry(
    main_frame, 
) 
urlField.grid(row=0, column=1)

statusLabel = tk.Label(
    main_frame, 
    text="Status: "
) 
statusLabel.grid(row=0, column=2)

status = tk.Label(
    main_frame, 
    text="Inactive",
    fg="red",
) 
status.grid(row=0, column=3)

### Second row ###
tokenLabel = tk.Label(
    main_frame, 
    text="Auth Token: "
) 
tokenLabel.grid(row=1, column=0)

# Token Textbox 
tokenField = tk.Entry(
    main_frame, 
) 
tokenField.grid(row=1, column=1)

### Third row ###
# Button Start 
startButton = tk.Button(
    main_frame,
    text="Start",
    command=None,  # Replace with your function
)
startButton.grid(row=3, column=0)

# Button Stop 
stopButton = tk.Button(
    main_frame,
    text="Stop",
    command=None,  # Replace with your function
)
stopButton.grid(row=3, column=1)

### Fourth row ###
printersLabel = tk.Label(
    list_frame, 
    text="Printers:"
) 
printersLabel.grid(row=0, column=0, sticky="w")

printers_list = tk.Listbox(list_frame)
printers_list.grid(row=1, column=0, sticky="ew")

root.mainloop()

################################################################
######################### Building GUI #########################
################################################################