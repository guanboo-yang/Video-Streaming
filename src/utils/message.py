# http request parser
import io


class HttpRequest:
    def __init__(self):
        self.method: str = ""
        self.path: str = ""
        self.version: str = ""
        self.headers: dict = {}
        self.body: bytes = b""

    def parse(self, rfile: io.BufferedReader):
        line = rfile.readline().decode()
        if line == "":
            raise ConnectionResetError
        self.method, self.path, self.version = line.rstrip().split(" ")

        headers = dict()
        while True:
            line = rfile.readline().decode()
            if line == "\r\n":
                break
            key, value = line.rstrip().split(": ")
            headers[key] = value
        self.headers = headers

        # check if there is a body
        if "Content-Length" not in self.headers:
            return

        length = int(self.headers["Content-Length"])
        body = rfile.read(length)
        self.body = body
        return

    # for debugging
    def __str__(self):
        ret = self.method + " " + self.path + " " + self.version + "\r\n"
        for key, value in self.headers.items():
            ret += key + ": " + value + "\r\n"
        ret += "\r\n"
        ret += self.body
        return ret
