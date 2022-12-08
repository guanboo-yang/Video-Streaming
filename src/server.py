import datetime
import io
import shutil
import socket
import threading
import os
import sys
import mimetypes

from utils.status import HttpStatus
from utils.message import HttpRequest, HttpResponse

BUFSIZE = 8192
BASIC_TEMPLATE = "<!DOCTYPE html>\n<html>\n<head>\n    <title>{0}</title>\n</head>\n<body>\n    <h1>{0}</h1>\n    <p>{1}</p>\n</body>\n</html>\n"


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class Server:
    def __init__(self, addr: str, port: int, Handler: "Handler", clinet_timeout: int = 60, root="dist", max_conn=50):
        self.addr = addr
        self.port = port
        self.Handler = Handler
        self.root = root
        self.max_conn = max_conn
        self.client_timeout = clinet_timeout

        # create server socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.addr, self.port))
        self.socket.listen(self.max_conn)

        # get hostname and ip address
        self.hostname = socket.gethostname()
        self.ip = socket.gethostbyname(self.hostname)

        eprint(f"Server starts, socket created at http://{self.ip}:{self.port} (sock_fd = {self.socket.fileno()})")
        eprint("---------------------------------------")

    def get_handler(self):
        return self.Handler(self.root, self.client_timeout)

    def mainloop(self):
        try:
            while True:
                client, addr = self.socket.accept()
                handler = self.get_handler()
                thread = threading.Thread(target=handler, args=(client, addr), daemon=True, name=client.fileno())
                eprint(f"\033[32mThread {thread.name} created, total: {threading.active_count()}\033[0m")
                thread.start()

        except KeyboardInterrupt:
            eprint("\rServer shutting down...")
            self.socket.close()
            sys.exit(0)


class Handler:
    def __init__(self, root: str, client_timeout=60):
        self.fd = 0
        self.root = root
        self.client: socket.socket = None
        self.rfile: io.BufferedReader = None
        self.wfile: io.BufferedWriter = None
        self.request: HttpRequest = None
        self.client_timeout = client_timeout

        # headers to be sent
        self.headers: bytes

    def __call__(self, client, addr):
        try:
            self.tid = threading.current_thread().name
            self.client = client
            self.rfile = client.makefile("rb", -1)
            self.wfile = client.makefile("wb", 0)
            self.addr = addr

            # set timeout
            self.client.settimeout(self.client_timeout)

            eprint(f"\033[32mAccept new connection from {self.addr[0]}:{self.addr[1]} (tid={self.tid})\033[0m")

            while True:
                # handle one request
                self.request = HttpRequest()
                self.request.parse(self.rfile)

                method_name = "handle_" + self.request.method.lower()
                if not hasattr(self, method_name):
                    response = HttpResponse()
                    response.set_error(HttpStatus.NOT_IMPLEMENTED)
                    self.send_response(response)
                    continue
                method = getattr(self, method_name)
                method()

                self.rfile.flush()
                self.wfile.flush()

        except Exception as e:
            self.pre_terminate(e)
            return

    def pre_terminate(self, exception_type):
        if type(exception_type) in (ConnectionResetError, BrokenPipeError, socket.timeout):
            eprint(f"\033[31mConnection closed {self.addr[0]}:{self.addr[1]} (tid={self.tid})\033[0m")
        else:
            eprint(f"\033[31m{exception_type} (tid={self.tid})\033[0m")
        self.rfile.close()
        self.wfile.close()
        self.client.close()

    def send_response(self, response: HttpResponse):
        self.wfile.write(response.encode())
        if response.is_file_body:
            with open(response.body_file_path, "rb") as f:
                shutil.copyfileobj(f, self.wfile)