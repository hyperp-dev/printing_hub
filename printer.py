import socket
import os
import pdfkit

class Printer:
    def __init__(
            self,
            content: str,
            ip: str,
            port: int = 9100,
        ):
        
        self.content = content
        self.ip = ip
        self.port = port

     ## Returns true if printing was successful
    ## and false otherwise
    def print(self) -> bool:
        
        """
        After saving html file (temp_file_path), the file needs to be
        converted to raw format such as pdf file
        """
        
        file_path = self.convert_to_pdf()

        # Read the contents of the pdf file
        with open(file_path, 'rb') as file:
            file_data = file.read()

        # Create a socket connection to the printer
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # Connect to the printer's IP address and port
                s.connect((self.ip, self.port))

                # Send the file data to the printer
                s.sendall(file_data)

                print("File sent to the printer successfully.")

                ## Remove temp file
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                return True
            
        except Exception as e:
            print(f"Failed to print: {e}")

            return False
        
    def convert_to_pdf(self) -> str:
        with open("test.html", "w", encoding="utf-8") as temp_file:
            temp_file.write(self.content)

        file_path = "templates/out.pdf"
        options = {
         'encoding': "UTF-8",
         'custom-header' : [
            ('Accept-Encoding', 'gzip')
         ],
         'no-outline': None,
    }
        is_converted = pdfkit.from_file("test.html", file_path, options=options)

        if is_converted:
            return file_path
        
        else:
            return None