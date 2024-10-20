import requests

class PrintRequest:
    
    def __init__(
            self,
            seq_no: int = None,
            tenant_id: int = None,
            location_code: str = None,
            day_no: int = None,
            data: str = None,
            printer_name: str = None,
            ticket_queue_seq: str = None,
            cash_drawer_code: str = None,
            open_cash_drawer: int = None,
        ):
        
        self.seq_no = seq_no
        self.tenant_id = tenant_id
        self.location_code = location_code
        self.day_no = day_no
        self.data = data
        self.printer_name = printer_name
        self.ticket_queue_seq = ticket_queue_seq
        self.cash_drawer_code = cash_drawer_code
        self.open_cash_drawer = open_cash_drawer


    ## Convert json (dict) to PrintRequest object
    def from_json(self, data: dict):
        return PrintRequest(
            seq_no = data["seq_no"],
            tenant_id = data["tenant_id"],
            location_code = data["location_code"],
            day_no = data["day_no"],
            data = data["printing_data"],
            printer_name = data["printer_name"],
            ticket_queue_seq = data["ticket_queue_seq"],
            cash_drawer_code = data["open_cash_drawer_code"],
            open_cash_drawer = data["open_cash_drawer"],
        )
