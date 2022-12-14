# http request parser
import io
from utils.status import HttpStatus
import datetime
import mimetypes
import os

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
    def __init__(self, version: str="HTTP/1.1", cors=None, ranges=False):
        self.version: str = version
        self.status_code: int = ""
        self.status_msg: str = ""
        self.status_line: str = ""
        self.headers: dict = {}
        self.body: bytes = b""
        self.is_file_body: bool = False
        self.body_file_path: str = ""

        # some default headers
        self.add_header("Server", "Project Demo for NTU CSIE Computer Network course")
        self.add_header("Date", datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"))
        self.add_header("Access-Control-Allow-Credentials", "true")
        if ranges:
            self.add_header("Accept-Ranges", "bytes")

        if cors is not None:
            self.add_header("Access-Control-Allow-Origin", cors)

    def __str__(self):
        ret = self.status_line
        for key, value in self.headers.items():
            ret += key + ": " + value + "\r\n"
        ret += "\r\n"
        return ret

    def set_status(self, status: HttpStatus):
        self.status_code = status.code
        self.status_msg = status.reason
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

            if partial_range is not None:

                file_size = os.path.getsize(file_path)
                file_type = self.get_mime_type(file_path)

                # multirange
                if len(partial_range) > 1:
                    boundary = "3d6b6a416f9b5" # from mozilla

                    self.add_header("Content-Type", "multipart/byteranges; boundary=" + boundary)

                    for r in partial_range:
                        if r[1] == -1:
                            r[1] = file_size - 1

                        self.body += ("--" + boundary + "\r\n").encode()
                        self.body += ("Content-Type: " + file_type + "\r\n").encode()
                        self.body += ("Content-Range: bytes " + str(r[0]) + "-" + str(r[1]) + "/" + str(file_size) + "\r\n\r\n").encode()

                        f.seek(r[0], 0)
                        self.body += f.read(r[1] - r[0] + 1)
                    
                    self.body += ("--" + boundary + "--\r\n").encode()

                    self.add_header("Content-Length", str(len(self.body)))
                
                # single range
                elif len(partial_range) == 1:
                    start = partial_range[0][0]
                    end = partial_range[0][1]

                    if end == -1:
                        end = file_size - 1

                    self.add_header("Content-Range", "bytes " + str(start) + "-" + str(end) + "/" + str(file_size))
                    self.add_header("Content-Length", str(end - start + 1))

                    f.seek(start, 0)
                    self.body = f.read(end - start + 1)
                    self.add_header("Content-Type", file_type)

                # write body to tmp file: dist/videos/tmp
                tmp_file_path = "dist/tmp"
                tmp_file = open(tmp_file_path, "wb")
                tmp_file.write(self.body)
                tmp_file.close()

                self.body = b""

                self.body_file_path = tmp_file_path
                self.is_file_body = True

                f.close()
                return HttpStatus.PARTIAL_CONTENT

            else:
                # file exists
                fsize = os.path.getsize(file_path)
                self.body_file_path = file_path
                self.is_file_body = True

                self.add_header("Content-Length", str(fsize))
                self.add_header("Content-Type", self.get_mime_type(file_path))
                
                f.close()
                return HttpStatus.OK
        else:
            self.is_file_body = False

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

        if self.is_file_body == False:
            ret += self.body

        return ret