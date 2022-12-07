import datetime
import io
import shutil
import signal
import socket
import threading
import os
import sys
import mimetypes

from utils.status import HttpStatus
from utils.message import HttpRequest

BUFSIZE = 8192
BASIC_TEMPLATE = "<!DOCTYPE html>\n<html>\n<head>\n    <title>{0}</title>\n</head>\n<body>\n    <h1>{0}</h1>\n    <p>{1}</p>\n</body>\n</html>\n"


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class Server:
    def __init__(self, addr: str, port: int, Handler: "Handler", root="dist", max_conn=50):
        self.addr = addr
        self.port = port
        self.Handler = Handler
        self.root = root
        self.max_conn = max_conn

        # create server socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.addr, self.port))
        self.server.listen(self.max_conn)

        # get hostname and ip address
        self.hostname = socket.gethostname()
        self.ip = socket.gethostbyname(self.hostname)

        eprint(f"Server created at http://{self.ip}:{self.port} ({self.server.fileno()})")
        eprint("---------------------------------------")

    def run_forever(self):
        try:
            while True:
                client, addr = self.server.accept()
                handler = self.Handler(self.root)
                thread = threading.Thread(target=handler, args=(client, addr), daemon=True, name=client.fileno())
                thread.start()
                # eprint("Pylance: Code is unreachable")
        except KeyboardInterrupt:
            eprint("\rServer shutting down...")
            self.server.close()
            sys.exit(0)


class Handler:
    def __init__(self, root: str):
        self.fd = 0
        self.root = root
        self.client: socket.socket = None
        self.rfile: io.BufferedReader = None
        self.wfile: io.BufferedWriter = None
        self.request: HttpRequest = None
        # headers to be sent
        self.headers: bytes

    def __call__(self, client: socket.socket, addr: tuple[str, int]):
        try:
            self.fd = threading.current_thread().name
            self.client = client
            self.rfile = client.makefile("rb", -1)
            self.wfile = client.makefile("wb", 0)
            # should we use timeout?
            # client.settimeout(2)
            eprint(f"\033[32mNew connection from {addr[0]}:{addr[1]} ({self.fd})\033[0m")

            while True:
                # handle one request
                self.request = HttpRequest()
                self.request.parse(self.rfile)
                method_name = "handle_" + self.request.method.lower()
                if not hasattr(self, method_name):
                    self.send_error(HttpStatus.NOT_IMPLEMENTED)
                    continue
                method = getattr(self, method_name)
                method()
                self.rfile.flush()
                self.wfile.flush()
        except (ConnectionResetError, BrokenPipeError, TimeoutError):
            self.exit_thread()
        except Exception as e:
            eprint(f"\033[31m{e}\033[0m")
            self.exit_thread()

    def exit_thread(self):
        eprint(f"\033[31mConnection closed ({self.fd})\033[0m")
        # eprint(f"Active threads: {threading.active_count() - 1}")
        # eprint([t.name for t in threading.enumerate()])
        self.client.close()
        sys.exit(0)

    def handle_get(self):
        file_str = self.root + self.request.path

        if file_str.endswith("/"):
            file_str += "index.html"

        # for single-page application
        # if file_str.find(".") == -1:
        #     file_str = self.root + "/index.html"

        try:
            f = open(file_str, "rb")
        except FileNotFoundError:
            eprint(f"GET {self.request.path} 404 Not Found")
            self.send_error(HttpStatus.NOT_FOUND)
            return
        except PermissionError:
            eprint(f"GET {self.request.path} 403 Forbidden")
            self.send_error(HttpStatus.FORBIDDEN)
            return
        except:
            eprint(f"GET {self.request.path} 500 Internal Server Error")
            self.send_error(HttpStatus.INTERNAL_SERVER_ERROR)
            return

        # 200 OK
        self.send_response(HttpStatus.OK)
        self.send_header("Content-Type", self.get_mime_type(file_str))
        self.send_header("Content-Length", size := os.path.getsize(file_str))
        # eprint(f"File Size: {size} bytes")
        self.end_headers()

        # send file
        shutil.copyfileobj(f, self.wfile)
        # res.body = f.read()

        # TODO: partial content if range is specified
        if "Range" in self.request.headers:
            pass

        # self.wfile.write(res.body)
        f.close()
        return

    def send_response(self, status: HttpStatus):
        self.headers = b""
        self.headers += f"{self.request.version} {status}\r\n".encode()
        self.send_header("Server", "Project Demo for NTU CSIE Computer Network course")
        self.send_header("Date", datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"))
        # eprint(f"{self.request.method} {self.request.path} {status} ({self.fd})")
        eprint(f"\033[33m{self.request.method}\033[0m {self.request.path} {status} ({self.fd})")
        return

    def send_header(self, key: str, value: str):
        self.headers += f"{key}: {value}\r\n".encode()
        return

    def end_headers(self):
        self.headers += b"\r\n"
        self.wfile.write(self.headers)
        self.wfile.flush()
        return

    def send_error(self, status: HttpStatus):
        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        error_page = self.root + "/error/" + str(status.code) + ".html"

        try:
            f = open(error_page, "rb")
        except:
            reason = status.reason
            description = status.description
            body = BASIC_TEMPLATE.format(reason, description).encode()
        else:
            body = f.read()
            f.close()

        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        return

    def get_mime_type(self, file: str) -> str:
        mime, encoding = mimetypes.guess_type(file)
        return mime
