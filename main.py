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


## Global variables
base_url = None
is_running = False
auth_token = None


## Start the service
def start():
    global is_running
    is_running = True
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
                    temp_file_path = save_temp_file(seq_no, template_content)

                    ## HTML file is saved
                    if temp_file_path is not None and os.path.exists(temp_file_path):
                        port = 9100 ## Default port
                        
                        is_printed = print_to_printer(printer_ip, port, temp_file_path)

                        if is_printed:
                            ## update printing sequence
                            update_queue(seq_no)

                        else:
                            ## show error
                            pass

                ## Printer was not found
                else:
                    pass
                    # Send error message
                    

                ## Wait n of seconds between printing
                time.sleep(3)

                if not is_running:
                    break

        ## Wait n of seconds before fetching new orders
        time.sleep(5)


## Stop the service
def stop():
    global is_running
    is_running = False
    print("The service is stopped")

def os_name() -> str:
    return platform.system()


def save_temp_file(seq_no: int, template_content: str):
    try:
        file_path = f"templates/temp_{seq_no}.html"

        with open(file_path, "w", encoding="utf-8") as temp_file:
            temp_file.write(template_content)
        return file_path
        
    except:
        return None



def find_printer(printer_name: str) -> str:
    if os_name() == "Windows":
        return get_printer_ip_windows(printer_name)
    
    elif os_name == "Linux":
        return get_printer_ip_linux(printer_name)


def open_cash_drawer(printer_socket):
    # ESC d p t command to open cash drawer (first drawer)
    command = bytes([0x1B, 0x64, 0x00, 0x1E])
    printer_socket.sendall(command)


## Returns true if printing was successful
## and false otherwise
def print_to_printer(printer_ip: str, port: int, temp_file_path: str) -> bool:
    
    """
       After saving html file (temp_file_path), the file needs to be
       converted to raw format such as pdf file
    """

    file_path = ""
    
    # Read the contents of the file
    with open(file_path, 'rb') as file:
        file_data = file.read()

    # Create a socket connection to the printer
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Connect to the printer's IP address and port
            s.connect((printer_ip, port))

            # Send the file data to the printer
            s.sendall(file_data)

            print("File sent to the printer successfully.")

            ## Remove temp file
            if os.path.exists(file_path):
                os.remove(file_path)

            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            
            return True
        
    except Exception as e:
        print(f"Failed to print: {e}")

        return False
    

def update_queue(seq_no: int):
    url = f"{base_url}{UPDATE_QUEUE_URL}{seq_no}"
    api_client = ApiClient(url=url, method="PUT")

    response = api_client.execute()

    if response["success"]:
        pass


## Save server base url in local memory
## then starts the service
def set_api_url():
    global base_url
    global auth_token

    base_url = urlField.get(1.0, "end-1c")
    auth_token = tokenField.get(1.0, "end-1c") 

    lbl.config(text = "Provided Input: "+auth_token)

    ## Run the service in a different thread to not block GUI functionalities
    thread = threading.Thread(target=start, daemon=True)
    thread.start()


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
    pass


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

center_window(root, 700, 550)

# URL Textbox
urlField = tk.Text(
    root, 
    height = 5, 
    width = 20,
) 

urlField.pack()


# Token Textbox 
tokenField = tk.Text(
    root, 
    height = 1, 
    width = 20,
) 

tokenField.pack() 

# Button Start 
printButton = tk.Button(
    root,
    text = "Start",
    command = set_api_url,
) 
printButton.pack()

# Button Stop 
printButton = tk.Button(
    root,
    text = "Stop",
    command = stop,
) 
printButton.pack() 

# Label Creation 
lbl = tk.Label(root, text = "") 
lbl.pack()

root.mainloop()

################################################################
######################### Building GUI #########################
################################################################