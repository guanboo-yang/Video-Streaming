# http request and response
class http_request:
    def __init__(self):
        self.method: str = ""
        self.path: str = ""
        self.version: str = ""
        self.headers: dict = {}
        self.body: str = ""
    
    def to_string(self):
        # convert this object to string
        ret = self.method + " " + self.path + " " + self.version + "\r\n"
        for key, value in self.headers.items():
            ret += key + ": " + value + "\r\n"
        ret += "\r\n"
        ret += self.body
        return ret

class http_response:
    def __init__(self):
        self.version: str = ""
        self.status_code: int = ""
        self.status_msg: str = ""
        self.headers: dict = {}
        self.body: str = ""
    
    def to_string(self, no_body=False):
        # convert this object to string
        ret = self.version + " " + str(self.status_code) + " " + self.status_msg + "\r\n"
        for key, value in self.headers.items():
            ret += key + ": " + value + "\r\n"
        ret += "\r\n"
        if not no_body:
            ret += self.body
        return ret