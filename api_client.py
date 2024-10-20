import requests


class ApiClient():
    def __init__(self, url: str, method: str, data=None, headers=None):
        self.url = url
        self.method = method.upper()
        self.data = data
        self.headers = headers


    ## Execute api request from the server
    def execute(self) -> dict:
        if self.method == "GET":
            response = requests.get(self.url, headers=self.headers)

        elif self.method == "POST":
            response = requests.put(self.url, json=self.data, headers=self.headers)

        elif self.method == "PUT":
            response = requests.put(self.url, json=self.data, headers=self.headers)

        elif self.method == "DELETE":
            response = requests.put(self.url, json=self.data, headers=self.headers)
            

        if response.status_code == 200:
            return {"status": response.status_code, "success": True, "data": response.json()}
        
        else:
            return {"status": response.status_code, "success": False, "data": response.json()}