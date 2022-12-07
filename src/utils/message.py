# http request parser
import io
from utils.status import HttpStatus
import datetime
import mimetypes

BASIC_TEMPLATE = "<!DOCTYPE html>\n<html>\n<head>\n    <title>{0}</title>\n</head>\n<body>\n    <h1>{0}</h1>\n    <p>{1}</p>\n</body>\n</html>\n"

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

class HttpResponse:
    def __init__(self):
        self.version: str = "HTTP/1.1"
        self.status_code: int = ""
        self.status_msg: str = ""
        self.status_line: str = ""
        self.headers: dict = {}
        self.body: bytes = b""

        # some default headers
        self.add_header("Server", "Project Demo for NTU CSIE Computer Network course")
        self.add_header("Date", datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"))

    def set_status(self, status: HttpStatus):
        self.status_code = status.value
        self.status_msg = status.name
        self.status_line = f"{self.version} {self.status_code} {self.status_msg}\r\n"

    def set_error(self, status: HttpStatus, root: str="dist"):
        self.set_status(status)
        self.add_header("Content-Type", "text/html")
        self.body = f"{self.status_code} {self.status_msg}\r\n"

        err_file = root + "/error/" + str(self.status_code) + ".html"

        try:
            f = open(err_file, "rb")
        except:
            self.body = BASIC_TEMPLATE.format(self.status_code, self.status_msg).encode()
        else:
            self.body = f.read().encode()
            f.close()

        self.add_header("Content-Length", str(len(self.body)))

    def add_header(self, key: str, value):
        self.headers[key] = value

    def set_body(self, file_path: str = None, partial_range: list = None, json_str: str = None):
        if file_path:
            try:
                f = open(file_path, "rb")
            except FileNotFoundError:
                return HttpStatus.NOT_FOUND
            except PermissionError:
                return HttpStatus.FORBIDDEN
            except:
                return HttpStatus.INTERNAL_SERVER_ERROR

            if partial_range:
                pass
            else:
                self.body = f.read()
                f.close()
                self.add_header("Content-Length", str(len(self.body)))
                self.add_header("Content-Type", self.get_mime_type(file_path))
                return HttpStatus.OK
        else:
            self.body = json_str.encode()
            self.add_header("Content-Length", str(len(self.body)))
            self.add_header("Content-Type", "application/json")
            return HttpStatus.OK


    def get_mime_type(self, file: str) -> str:
        mime, encoding = mimetypes.guess_type(file)
        return mime

    def encode(self):
        ret = self.status_line.encode()
        for key, value in self.headers.items():
            ret += f"{key}: {value}\r\n".encode()
        ret += b"\r\n"
        ret += self.body
        return ret
